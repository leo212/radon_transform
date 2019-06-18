import time
import numpy as np
from scipy import sparse
import sys
from skimage import measure
from skimage import io
from threading import Thread


def get_matrix_filename(algorithm, variant, size):
    return "radon_server/static/npz/" + algorithm + "." + variant + "." + str(size) + ".npz"


class RadonTransformThread(Thread):
    def __init__(self, action="transform", variant=None, args=None, method="direct"):
        if args is None:
            self.args = {}
        else:
            self.args = args

        self.should_update_progress = True
        self.action = action
        self.progress = 0
        self.took = 0
        self.cond = 0
        self.startTime = time.time()
        self.radon = None
        self.reconstructed = None
        self.variant = variant
        self.ratio = self.get_matrix_ratio()
        self.matrix = None
        self.matrix_size = 0
        self.similarity = None
        self.method = method
        self.error = None
        self.reconstruct_multiply = self.get_reconstruct_multiply()
        self.size = 0
        self.started = False

        super(RadonTransformThread, self).__init__()

    # override those methods
    def get_algorithm_name(self):
        return ""

    def get_matrix_ratio(self):
        return 1

    def get_reconstruct_multiply(self):
        return 255

    def run_transform(self, image, n, variant=None):
        pass

    def need_matrix(self):
        return True

    def run_build_matrix(self, n, variant):
        try:
            cols = []
            progress = 0
            for i in range(n):
                for j in range(n):
                    x = np.zeros((n, n), dtype=np.float64)
                    x[i, j] = 255
                    self.should_update_progress = False
                    self.run_transform(x, n, variant)
                    self.should_update_progress = True
                    rx = self.radon
                    nn = (n * self.ratio * n * self.ratio)
                    col = sparse.coo_matrix((np.reshape(rx, (nn)), (np.arange(nn), np.zeros(nn))))
                    cols.append(col)
                    progress += 1
                    self.matrix_size = sys.getsizeof(cols)
                    self.update_progress(progress, n * n)

            self.matrix = sparse.hstack(cols)
        except Exception as e:
            self.update_progress(100, 100)
            self.error = e


    def calculate_reconstructed_score(self):
        original_image = io.imread(self.args["original_file"], flatten=True).astype('float64')
        self.similarity = measure.compare_ssim(original_image, self.reconstructed, data_range=255)

    def get_matrix(self, variant, n):
        # load matrix file
        matrix_filename = get_matrix_filename(self.get_algorithm_name(), variant, n)
        A = sparse.load_npz(matrix_filename)
        AT = A.transpose()
        return A, AT

    def reconstruct_callback(self, xk):
        # evaluate progress by comparing to the last reconstructed image
        progress = measure.compare_ssim(np.reshape(xk, (self.size, self.size)) * self.reconstruct_multiply, self.reconstructed, data_range=255) * 100
        if progress > self.progress:
            self.progress = progress
        self.took = (time.time() - self.startTime) * 1000
        self.reconstructed = np.reshape(xk, (self.size, self.size)) * self.reconstruct_multiply
        self.calculate_reconstructed_score()

    def run_reconstruct(self, image, n, variant=None):
        try:
            (A, AT) = self.get_matrix(variant, n)

            # reconstruct
            self.size = n
            R = np.reshape(image, (n * n * self.ratio * self.ratio))

            if self.method == "direct":
                reconstructed = sparse.linalg.spsolve(AT * A, AT * R)
            elif self.method == "lsqr":
                reconstructed = sparse.linalg.lsqr(A, R, atol=self.args["tolerance"], btol=self.args["tolerance"])[0]
            elif self.method == "gmres":
                reconstructed = sparse.linalg.gmres(AT * A, AT * R, tol=self.args["tolerance"], callback=self.reconstruct_callback)[0]
            elif self.method == "cg":
                reconstructed = sparse.linalg.cgs(AT * A, AT * R, tol=self.args["tolerance"], callback=self.reconstruct_callback)[0]
            elif self.method == "qmr":
                reconstructed = sparse.linalg.qmr(AT * A, AT * R, tol=self.args["tolerance"], callback=self.reconstruct_callback)[0]
            else:
                raise Exception("Unsupported reconstruction method " + self.method)

            self.reconstructed = np.reshape(reconstructed, (self.size, self.size)) * self.reconstruct_multiply
            self.calculate_reconstructed_score()
            self.update_progress(100, 100)
        except Exception as e:
            self.update_progress(100, 100)
            self.error = e

    def start_algorithm(self, image, n, variant, action):
        try:
            if action == "transform":
                self.radon = np.zeros((n, n), dtype='float64')
                self.run_transform(image, n, variant)
            elif action == "build_matrix":
                self.run_build_matrix(n, variant)
                sparse.save_npz(
                    get_matrix_filename(self.get_algorithm_name(), self.variant, n),
                    self.matrix)
            elif action == "reconstruct":
                self.reconstructed = np.zeros((n, n), dtype='float64')
                self.run_reconstruct(image, n, variant)

            self.took = (time.time() - self.startTime) * 1000
        except Exception as e:
            self.update_progress(100, 100)
            self.error = e

    def save(self):
        if self.action == "transform":
            # save an image file for preview the radon transform
            io.imsave(self.args["target_image"], self.radon)

            # save the radon file itself
            np.save(self.args["target_file"], self.radon)

            # calculate the cond value of the matrix
            (w, v) = np.linalg.eig(self.radon.transpose() * self.radon)
            self.cond = np.sqrt(np.max(np.real(v)) - np.min(np.real(v)))
        elif self.action == "reconstruct":
            io.imsave(self.args["target_file"], self.reconstructed)

    def update_progress(self, step, total_steps):
        if self.should_update_progress:
            self.progress = step * 100 / total_steps
            self.took = (time.time() - self.startTime) * 1000

    def run(self):
        image = None
        n = 0

        if self.action == "transform":
            print(self.get_algorithm_name() + " started for " + self.args["source_file"])
            # load image file from disk
            image = io.imread(self.args["source_file"], flatten=True).astype('float64')
            n = int(np.shape(image)[0])

        elif self.action == "build_matrix":
            print("build matrix started for " + self.get_algorithm_name())
            n = self.args["size"] // self.ratio

        elif self.action == "reconstruct":
            print("image reconstruction started for " + self.args["source_file"])
            image = np.load(self.args["source_file"])
            n = len(image) // self.ratio

        self.startTime = time.time()
        self.start_algorithm(image, n, self.variant, self.action)
        print(self.get_algorithm_name() + " " + self.action + " took:" + str(self.took) + "ms")
        self.progress = 100

        # save transform image file
        self.save()

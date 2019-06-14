import time
import numpy as np
from scipy import misc, sparse
import sys
from skimage.measure import compare_ssim as ssim
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
        self.ratio = 1
        self.matrix = None
        self.matrix_size = 0
        self.similarity = None
        self.method = method

        super(RadonTransformThread, self).__init__()

    # override those methods
    def get_algorithm_name(self):
        return ""

    def run_transform(self, image, n, variant=None):
        pass

    def need_matrix(self):
        return True

    def run_build_matrix(self, n, variant):
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

    def calculate_reconstructed_score(self):
        original_image = misc.imread(self.args["original_file"], flatten=True).astype('float64')
        self.similarity = ssim(original_image, self.reconstructed, data_range=255)
        print(self.similarity)

    def run_reconstruct(self, image, n, variant=None):
        # load matrix file
        matrix_filename = get_matrix_filename(self.get_algorithm_name(), variant, n)
        A = sparse.load_npz(matrix_filename)

        # reconstruct
        R = np.reshape(image, (n * n * self.ratio * self.ratio))

        if self.method == "direct":
            reconstructed = sparse.linalg.spsolve(A.transpose()*A, A.transpose()*R)
        elif self.method == "lsqr":
            reconstructed = sparse.linalg.lsqr(A, R, atol=1e-06, btol=1e-06)[0]
        elif self.method == "cg":
            reconstructed = sparse.linalg.cgs(A.transpose() * A, A.transpose() * R, tol=1e-05)[0]

        self.reconstructed = np.reshape(reconstructed, (n, n)) * 255
        self.calculate_reconstructed_score()
        self.update_progress(100, 100)

    def start_algorithm(self, image, n, variant, action):
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

    def save(self):
        if self.action == "transform":
            # save an image file for preview the radon transform
            misc.imsave(self.args["target_image"], self.radon)

            # save the radon file itself
            np.save(self.args["target_file"], self.radon)

            # calculate the cond value of the matrix
            (w, v) = np.linalg.eig(self.radon.transpose() * self.radon)
            self.cond = np.sqrt(np.max(np.real(v)) - np.min(np.real(v)))
        elif self.action == "reconstruct":
            misc.imsave(self.args["target_file"], self.reconstructed)

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
            image = misc.imread(self.args["source_file"], flatten=True).astype('float64')
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

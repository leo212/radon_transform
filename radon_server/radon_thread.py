import time
import numpy as np
from scipy import misc, sparse
import sys
from threading import Thread


class RadonTransformThread(Thread):
    def __init__(self, action="transform", variant=None, args=None):
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

        super(RadonTransformThread, self).__init__()

    # override those methods
    def get_algorithm_name(self):
        return ""

    def run_transform(self, image, n, variant=None):
        pass

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

    def run_reconstruct(self, image, n, variant=None):
        # load matrix file
        matrix_filename = self.get_matrix_filename(self.get_algorithm_name(), variant, n)
        A = sparse.load_npz(matrix_filename)

        # reconstruct
        R = np.reshape(image, (n * n * self.ratio * self.ratio))

        # XCG = sparse.linalg.cg(A.transpose() * A, A.transpose() * R)[0]
        XC2 = sparse.linalg.lsqr(A, R)[0]
        self.reconstructed = np.reshape(XC2, (n, n))
        self.update_progress(100,100)

    def start_algorithm(self, image, n, variant, action):
        if action == "transform":
            self.radon = np.zeros((n, n), dtype='float64')
            self.run_transform(image, n, variant)
        elif action == "build_matrix":
            self.run_build_matrix(n, variant)
            sparse.save_npz(
                self.get_matrix_filename(self.get_algorithm_name(), self.variant, n),
                self.matrix)
        elif action == "reconstruct":
            self.reconstructed = np.zeros((n, n), dtype='float64')
            self.run_reconstruct(image, n, variant)

        self.took = (time.time() - self.startTime) * 1000

    def get_matrix_filename(self, algorithm, variant, size):
        return "radon_server/static/npz/" + algorithm + "." + variant + "." + str(size) + ".npz"

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

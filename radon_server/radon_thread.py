import time
import numpy as np
from scipy import misc
from threading import Thread


class RadonTransformThread(Thread):
    def __init__(self, source_file, target_file, variant=None):
        self.source_file = source_file
        self.target_file = target_file
        self.progress = 0
        self.took = 0
        self.cond = 0
        self.startTime = time.time()
        self.radon = None
        self.variant = variant

        super(RadonTransformThread, self).__init__()

    # override those methods
    def get_algorithm_name(self):
        return ""

    def run_algorithm(self, image, n, variant=None):
        pass

    def start_algorithm(self, image, n, variant):
        self.radon = np.zeros((n, n), dtype='float64')
        self.run_algorithm(image, n, variant)
        self.took = (time.time() - self.startTime) * 1000

    def save(self):
        misc.imsave(self.target_file, self.radon)
        # calculate the cond value of the matrix
        (w, v) = np.linalg.eig(self.radon.transpose() * self.radon)
        self.cond = np.sqrt(np.max(np.real(v)) - np.min(np.real(v)))

    def update_progress(self, step, total_steps):
        self.progress = step * 100 / total_steps
        self.took = (time.time() - self.startTime) * 1000

    def run(self):
        print(self.get_algorithm_name() + " started for " + self.source_file)
        image = misc.imread(self.source_file, flatten=True).astype('float64')
        n = int(np.shape(image)[0])

        self.startTime = time.time()
        self.start_algorithm(image, n, self.variant)
        print(self.get_algorithm_name() + " took:" + str(self.took) + "ms")
        self.progress = 100
        self.save()

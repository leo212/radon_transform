import time

import matplotlib.pyplot as plt
import numpy as np
from scipy import misc


def parallel_beam_image_rotation(image, steps):
    R = np.zeros((len(image), steps), dtype='float64')
    for s in range(steps):
        rotation = misc.imrotate(image, -float(s)*180/steps,interp="bilinear").astype('float64')
        R[:,s] = sum(rotation)
    return R

def test_pbim(filename):
    image = misc.imread(filename, flatten=True).astype('float64')
    n = np.shape(image)[0]

    start = time.time()
    radon0 = parallel_beam_image_rotation(image, n)
    duration =  time.time() - start
    print("parallel beam took:" + str(duration*1000) + "ms")

    # Plot the original and the radon transformed image
    plt.subplot(1, 2, 1), plt.imshow(image, cmap='gray')
    plt.xticks([]), plt.yticks([])
    plt.xlabel("Original Image")
    plt.subplot(1, 2, 2), plt.imshow(radon0, cmap='gray')
    plt.xticks([]), plt.yticks([])
    plt.xlabel("Parallel Beam Radon")

    plt.show()

test_pbim('phantom100x100.png')

import time

import matplotlib.pyplot as plt
import numpy as np
from scipy import misc


def slow_slant_stack(image, n):
    R = np.zeros((n*2, n*2), dtype='float64')
    k = np.fft.fftshift(np.arange(-n,n))

    kn = (np.arange(0,n) - n/2)
    paddedImage = np.pad(image, n/2, mode='constant')[n/2:n/2+n,:]
    fft_matrix = np.fft.fft(paddedImage)

    # horizontal lines
    for s in range(n):
        p = (float(s)-n/2)/float(n/2)
        shiftby_arr = kn * p
        shifted_fft_matrix = fft_matrix * np.exp(-1j*2*np.pi*k*shiftby_arr.reshape(n,1)/(n*2))
        skewed = np.fliplr(np.real(np.fft.ifft(shifted_fft_matrix)).astype('float64'))
        R[:,s+n] = np.roll(sum(skewed),1)

    # vertical lines
    rotatedImage = np.transpose(image)
    paddedImage = np.pad(rotatedImage, n/2, mode='constant')[n/2:n/2+n,:]
    fft_matrix = np.fft.fft(paddedImage)

    for s in range(n):
        p = (float(s+1)-n/2)/float(n/2)
        shiftby_arr = kn * p
        shifted_fft_matrix = fft_matrix * np.exp(-1j*2*np.pi*k*shiftby_arr.reshape(n,1)/(n*2))
        skewed = np.real(np.fft.ifft(shifted_fft_matrix)).astype('float64')
        R[:,n-s-1] = sum(skewed)

    R = R/(np.sqrt(2)*n)  # Normalization
    R = R*2*n
    return R

def shiftby(image, n, p):
    k = np.concatenate((range(0,(n*2)/2), range(int(-(n*2)/2),0)))
    fft_matrix = np.fft.fft(image)
    shiftby = (np.arange(0,n) - n/2) * p
    fft_matrix = fft_matrix * np.exp(-1j*2*np.pi*k*shiftby.reshape(n,1)/(n*2))
    result=np.real(np.fft.ifft(fft_matrix))
    return result

def testSss(image):
    image = misc.imread(image, flatten=True).astype('float64')
    n = np.shape(image)[0]

    start = time.time()
    radon0 = slow_slant_stack(image, n)
    duration =  time.time() - start
    print("SSS took:" + str(duration*1000) + "ms")

    # Plot the original and the radon transformed image
    plt.subplot(2, 1, 1), plt.imshow(image, cmap='gray')
    plt.xticks([]), plt.yticks([])
    plt.xlabel("Original Image")
    plt.subplot(2, 1, 2), plt.imshow(radon0, cmap='gray')
    plt.xticks([]), plt.yticks([])
    plt.xlabel("SSS Radon")

    plt.show()

def testShiftBy(filename,p):
    image = misc.imread(filename, flatten=True).astype('float64')
    n = np.shape(image)[0]

    start = time.time()
    paddedImage = np.pad(image, n/2, mode='constant')[n/2:n/2+n,:]
    simage = shiftby(paddedImage, n, p)
    duration =  time.time() - start
    print("shift by took:" + str(duration*1000) + "ms")

    # Plot the original and the radon transformed image
    plt.subplot(2, 1, 1), plt.imshow(image, cmap='gray')
    plt.xticks([]), plt.yticks([])
    plt.xlabel("Original Image")
    plt.subplot(2, 1, 2), plt.imshow(simage, cmap='gray')
    plt.xticks([]), plt.yticks([])
    plt.xlabel("Shifted Image")

    plt.show()

# testShiftBy("white100x100.png",-1.0)
# testSss("phantom16x16.png")

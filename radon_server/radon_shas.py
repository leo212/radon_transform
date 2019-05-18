import math

import matplotlib.pyplot as plt
import numpy as np
from scipy import misc


def build_factors_table(n):
    result = []
    for s in range(0, n):
        result.append(build_factors_table_for_p(n, (float(s)/n-0.5)*2))

    return result

def shas_radon(image, n):
    factors_table = build_factors_table(n)
    # start = time.time()
    radon = shas(image, n, factors_table)
    # radon0 = shas_cv2(image, n)
    # duration =  time.time() - start
    # print("SHAS took:" + str(duration*1000) + "ms")
    return radon

def shas(image, n, factors_table):
    R = np.zeros((n*2, n), dtype='float64')

    # horizontal lines
    for s in range(n/2):
        factors = factors_table[s*2]
        skewed = skewby(image, factors, True).astype('float64')
        R[:,s] = sum(np.transpose(skewed))

    # vertical lines
    for s in range(n/2, n):
        factors = factors_table[(s-n/2)*2]
        skewed = skewby(image, factors, False).astype('float64')
        R[:,n-s+n/2-1] = sum(np.transpose(skewed))
    return R

def shas_cv2(image, n):
    R = np.zeros((n*2, n), dtype='float64')

    # horizontal lines
    for s in range(n/2):
        skewed = cv2skewx(image, float(s*2)/n-0.5).astype('float64')
        R[:,s] = sum(skewed)

    # vertical lines
    for s in range(n/2):
        skewed = cv2skewy(image, float(s*2)/n-0.5).astype('float64')
        R[:,n-s-1] = np.flipud(sum(np.transpose(skewed)))
    return R


def build_factors_table_for_p(n, p):
    factors = np.zeros((0),dtype='float64')
    dxs = np.zeros((0),dtype='int')
    dys = np.zeros((0),dtype='int')
    lasty = 0.0

    if (p > 0):
        m = 1
    else:
        m = -1

    x = 0
    y = p * x

    # first pixel of the line is always 0,0
    dxs = np.append(dxs, 0)
    dys = np.append(dys, 0)

    while x<n and m*y<=n:
        # handle straight line
        if (p == 0):
            factor = 1
            dx = 1
            dy = 0
            lasty = y
            factors = np.append(factors, factor)
            dxs = np.append(dxs, dx)
            dys = np.append(dys, dy)

        while(m*lasty < m*y):
            if (math.trunc(y)==math.trunc(lasty)):
                factor = m*y - m*lasty
                lasty = y
                dx = 1
                dy = 0
            else:
                factor = math.floor(m*y)-m*lasty
                if (m == 1):
                    lasty = math.floor(y)
                else:
                    lasty = math.ceil(y)
                if (y == lasty):
                    dx = 1
                else:
                    dx = 0
                dy = m

            factors = np.append(factors, factor)
            dxs = np.append(dxs, dx)
            dys = np.append(dys, dy)

        x = x + 1
        y = p * x

    factors /= sum(factors)

    dxs = dxs[:-1]
    dys = dys[:-1]

    kx = abs(sum(dxs))
    ky = abs(sum(dys))

    dxstravel = np.cumsum(dxs)
    dystravel = np.cumsum(dys)

    # make all of the values positive
    if (sum(dys) < 0):
       dystravel+=ky

    result = (factors, dxstravel, dystravel, kx, ky)
    return result

def skewby(image, factors_table, horizontal=True):
    n = np.shape(image)[0]
    (factors, dxstravel, dystravel, kx, ky) = factors_table

    linesize = np.shape(factors)[0]
    result = np.zeros((n*2,linesize), dtype='float64')

    if (horizontal):
        paddedImage = np.pad(image, ky, mode='constant')[:,ky:ky+n]

        for j in range(0, n+ky):
            result[j+n/2-ky/2,:] = paddedImage[dystravel+j, dxstravel] * factors
    else:
        paddedImage = np.pad(image, ky, mode='constant')[ky:ky+n,:]

        for j in range(0, n+ky):
            result[n*2-(j+n/2-ky/2),:] = paddedImage[dxstravel, dystravel+j] * factors

    return result

import cv2
def cv2skewx(image, p):
    rows, cols = image.shape
    d = p * cols
    pts1 = np.float32(
        [[0, 0],
         [cols, 0],
         [cols, rows],
         [0, rows]]
    )
    pts2 = np.float32(
        [[d, 0],
         [cols+d, 0],
         [cols-d, rows],
         [0-d, rows]]
    )
    paddedImage = cv2.copyMakeBorder(image, 0, 0, cols/2, cols/2, cv2.BORDER_CONSTANT)
    M = cv2.getPerspectiveTransform(pts1,pts2)
    return cv2.warpPerspective(paddedImage, M, (cols*2, rows))

def cv2skewy(image, p):
    rows, cols = image.shape
    d = p * cols
    pts1 = np.float32(
        [[0, 0],
         [cols, 0],
         [cols, rows],
         [0, rows]]
    )
    pts2 = np.float32(
        [[0, d],
         [cols, -d],
         [cols, rows-d],
         [0, rows+d]]
    )
    paddedImage = cv2.copyMakeBorder(image, rows/2, rows/2, 0, 0, cv2.BORDER_CONSTANT)
    M = cv2.getPerspectiveTransform(pts1,pts2)
    return cv2.warpPerspective(paddedImage, M, (cols, rows*2))

def testSkew(image):
    image = misc.imread(image, flatten=True).astype('float64')
    n = np.shape(image)[0]

    factors_table = build_factors_table(n)
    p = 0.09
    skewedImage = skewby(image, build_factors_table_for_p(n,p))
    plt.subplot(1, 2, 1), plt.imshow(skewedImage, cmap='gray')
    plt.subplot(1, 2, 2), plt.imshow(cv2skewy(image, p), cmap='gray')

    plt.show()

def testShas(image):
    image = misc.imread(image, flatten=True).astype('float64')
    n = np.shape(image)[0]

    radon0 = shas_radon(image, n)

    # Plot the original and the radon transformed image
    plt.subplot(2, 1, 1), plt.imshow(image, cmap='gray')
    plt.xticks([]), plt.yticks([])
    plt.xlabel("Original Image")
    plt.subplot(2, 1, 2), plt.imshow(radon0, cmap='gray')
    plt.xticks([]), plt.yticks([])
    plt.xlabel("SHAS Radon")

    plt.show()

# testShas("black100x100.png")
# testShas("SheppLogan_Phantom.png")
#testShas("phantom100x100.png")
# image =misc.imread("lenna100x100.png", flatten=True).astype('float64')
# simage = cv2skewby(image, -0.3)
# plt.subplot(2,1,1);plt.imshow(image, cmap='gray')
# plt.subplot(2,1,2);plt.imshow(simage, cmap='gray')
# plt.show()

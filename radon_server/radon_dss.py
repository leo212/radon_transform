import math
import time

import numpy as np
from scipy import misc


def discrete_slant_stacking(image, n):
    M = int(np.shape(image)[0])
    N = int(np.shape(image)[1])
    radon = np.zeros((n, n), dtype='float64')

    # min_r = -math.sqrt(2*math.pow(n/2,2))
    # max_r = math.sqrt(2*math.pow(n/2,2))

    for h in range(0, n):
        # calculate radon for horizontal lines
        for k in range(0, int(n / 2)):
            theta = math.pi * 0.25 + (k * math.pi) / n
            # r = min_r + (max_r-min_r) * h / (n-1)
            r = h - n / 2
            x = np.array(range(int(-M / 2), int(M / 2)))
            y = (r - x * np.cos(theta)) / np.sin(theta)
            x += int(M / 2)
            y += int(N / 2)

            # calculate weights of line between pixels
            y1 = y.astype(int)
            w1 = 1 - (y - y1)
            y2 = (y + 1).astype(int)
            w2 = (y - y1)

            # cut out of bounds values
            # lower bound
            x = x[np.where(y1 >= 0)]
            w1 = w1[np.where(y1 >= 0)]
            w2 = w2[np.where(y1 >= 0)]
            y2 = y2[np.where(y1 >= 0)]
            y1 = y1[np.where(y1 >= 0)]

            # upper bound
            x = x[np.where(y2 < N)]
            w1 = w1[np.where(y2 < N)]
            w2 = w2[np.where(y2 < N)]
            y1 = y1[np.where(y2 < N)]
            y2 = y2[np.where(y2 < N)]

            radon[h, k] = (image[x, y1] * w1).sum() + (image[x, y2] * w2).sum()

            # slower implementation
            # sum = 0
            # for x in range(-M/2, M/2):
            #     y = ((r - x*math.cos(theta))/math.sin(theta))
            #
            #     y1 = int(y)
            #     w1 = 1-(y-y1)
            #     y2 = int(y+1)
            #     w2 = (y-y1)
            #
            #     if y1 >= -N/2 and y1<N/2:
            #         sum = sum + image[x+N/2, y1+M/2]*w1
            #     if y2 >= -N/2 and y2<N/2:
            #         sum = sum + image[x+N/2, y2+M/2]*w2
            # radon[h,k] = sum

        # calculate radon for vertical lines
        for k in range(0, int(n / 2)):
            theta = math.pi * 0.75 + (k * math.pi) / n
            # r = min_r + (max_r-min_r) * h / (n-1)
            r = h - n / 2
            y = np.array(range(int(-N / 2), int(N / 2)))
            x = (r - y * np.sin(theta)) / np.cos(theta)
            x += int(N / 2)
            y += int(M / 2)

            # calculate weights of line between pixels
            x1 = x.astype(int)
            w1 = 1 - (x - x1)
            x2 = (x + 1).astype(int)
            w2 = (x - x1)

            # cut out of bounds values
            # lower bound
            y = y[np.where(x1 >= 0)]
            w1 = w1[np.where(x1 >= 0)]
            w2 = w2[np.where(x1 >= 0)]
            x2 = x2[np.where(x1 >= 0)]
            x1 = x1[np.where(x1 >= 0)]

            # upper bound
            y = y[np.where(x2 < N)]
            w1 = w1[np.where(x2 < N)]
            w2 = w2[np.where(x2 < N)]
            x1 = x1[np.where(x2 < N)]
            x2 = x2[np.where(x2 < N)]

            radon[h, int(n / 2 + k)] = (image[x1, y] * w1).sum() + (image[x2, y] * w2).sum()

            # slower implementation
            # sum = 0
            # for y in range(-M/2, M/2):
            #         x=(r-y*math.sin(theta))/math.cos(theta)
            #         x1 = int(x)
            #         w1 = 1-(x-x1)
            #         x2 = int(x+1)
            #         w2 = (x-x1)
            #
            #         if x1 >= -N/2 and x1<N/2:
            #             sum = sum + image[x1+N/2, y+M/2]*w1
            #         if x2 >= -N/2 and x2<N/2:
            #             sum = sum + image[x1+N/2, y+M/2]*w2
            # radon[h,n/2+k] = sum
    return radon


# cartesian coordinates
def discrete_slant_stacking_cart(image, steps):
    H = steps
    K = steps

    pmin = -1
    tmin = 0
    dp = 0.02
    dt = 1
    p = np.arange(pmin, pmin + dp * H, dp, np.float)
    tau = np.arange(tmin, tmin + dt * K, dt, np.float)
    dx = 1
    dy = 1
    xmin = -math.floor(steps / 2)
    ymin = 0

    M = np.shape(image)[0]
    N = np.shape(image)[1]

    radon = np.zeros((H, K), dtype='float64')

    for k in range(0, K):
        for h in range(0, H):
            alpha = p[k] * dx / dy
            beta = (p[k] * xmin + tau[h] - ymin) / dy
            sum = 0
            for m in range(0, M):
                n = int(round(alpha * m + beta))
                if (n >= 0 and n < N):
                    sum = sum + image[n, m]
            radon[H - h - 1, K - k - 1] = sum
    return radon


def test_dss(image_file):
    image = misc.imread(image_file, flatten=True).astype('float64')
    n = int(np.shape(image)[0])

    start = time.time()
    radon1image = discrete_slant_stacking(image, n)
    duration = time.time() - start
    print("DSS took:" + str(duration * 1000) + "ms")

    misc.imsave("images/result.png", radon1image)

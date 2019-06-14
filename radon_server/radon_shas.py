import math

import cv2
import numpy as np
from radon_server.radon_thread import RadonTransformThread


class SHASTransform(RadonTransformThread):
    def __init__(self, action="transform", variant=None, args=None, method="direct"):
        super(SHASTransform, self).__init__(action, variant, args, method)
        self.ratio = 2


    def get_algorithm_name(self):
        return "shas"

    def run_transform(self, image, n, variant=None):
        self.radon = np.zeros((n * 2, n * 2), dtype='float64')
        self.shas_radon(image, n, variant)

    def build_factors_table(self, n):
        result = []
        for s in range(0, n):
            result.append(self.build_factors_table_for_p(n, (float(s) / n - 0.5) * 2))

        return result

    def shas_radon(self, image, n, variant):
        if variant == "cv2":
            self.shas_cv2(image, n)
        else:
            factors_table = self.build_factors_table(n)
            self.shas(image, n, factors_table)

    def shas(self, image, n, factors_table):
        # horizontal lines
        for s in range(n):
            factors = factors_table[s]
            skewed = self.skewby(image, factors, True).astype('float64')
            self.radon[:, s] = sum(np.transpose(skewed))
            self.update_progress(s, n * 2)

        # vertical lines
        for s in range(n):
            factors = factors_table[n - s - 1]
            skewed = self.skewby(image, factors, False).astype('float64')
            self.radon[:, n + s] = sum(np.transpose(skewed))
            self.update_progress(n + s, n * 2)

    def shas_cv2(self, image, n):
        # horizontal lines
        for s in range(n):
            skewed = self.cv2skewx(image, float(s / n - 0.5)).astype('float64')
            self.radon[:, n + (n - s - 1)] = np.roll(np.flipud(sum(skewed)), 1, 0)
            self.update_progress(s, n * 2)

        # vertical lines
        for s in range(n):
            skewed = self.cv2skewy(image, float((n-s-1) / n - 0.5)).astype('float64')
            self.radon[:, n - s - 1] = sum(np.transpose(skewed))
            self.update_progress(n + s, n * 2)

    def build_factors_table_for_p(self, n, p):
        factors = np.zeros(n, dtype='float64')
        dxs = np.zeros(n, dtype='int')
        dys = np.zeros(n, dtype='int')
        lasty = 0.0

        if p > 0:
            m = 1
        else:
            m = -1

        x = 0
        y = p * x

        # first pixel of the line is always 0,0
        dxs = np.append(dxs, 0)
        dys = np.append(dys, 0)

        while x < n and m * y <= n:
            # handle straight line
            if p == 0:
                factor = 1
                dx = 1
                dy = 0
                lasty = y
                factors = np.append(factors, factor)
                dxs = np.append(dxs, dx)
                dys = np.append(dys, dy)

            while m * lasty < m * y:
                if math.trunc(y) == math.trunc(lasty):
                    factor = m * y - m * lasty
                    lasty = y
                    dx = 1
                    dy = 0
                else:
                    factor = math.floor(m * y) - m * lasty
                    if m == 1:
                        lasty = math.floor(y)
                    else:
                        lasty = math.ceil(y)
                    if y == lasty:
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

        kx = abs(sum(dxs)).astype(int)
        ky = abs(sum(dys)).astype(int)

        dxstravel = np.array(np.cumsum(dxs)).astype(int)
        dystravel = np.array(np.cumsum(dys)).astype(int)

        # make all of the values positive
        if (sum(dys) < 0):
            dystravel += ky

        result = (factors, dxstravel, dystravel, kx, ky)
        return result

    def skewby(self, image, factors_table, horizontal=True):
        n = np.shape(image)[0]
        (factors, dxstravel, dystravel, kx, ky) = factors_table

        linesize = np.shape(factors)[0]
        result = np.zeros((n * 2, linesize), dtype='float64')

        if horizontal:
            padded_image = np.pad(image, ky, mode='constant')[:, ky:ky + n]

            for j in range(0, n + ky):
                result[j + n // 2 - ky // 2, :] = padded_image[dystravel + j, dxstravel] * factors
        else:
            padded_image = np.pad(image, ky, mode='constant')[ky:ky + n, :]

            for j in range(0, n + ky):
                result[n * 2 - (j + n // 2 - ky // 2), :] = padded_image[dxstravel, dystravel + j] * factors

        return result

    def cv2skewx(self, image, p):
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
             [cols + d, 0],
             [cols - d, rows],
             [0 - d, rows]]
        )
        padded_image = cv2.copyMakeBorder(image, 0, 0, cols // 2, cols // 2, cv2.BORDER_CONSTANT)
        M = cv2.getPerspectiveTransform(pts1, pts2)
        return cv2.warpPerspective(padded_image, M, (cols * 2, rows))

    def cv2skewy(self, image, p):
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
             [cols, rows - d],
             [0, rows + d]]
        )
        padded_image = cv2.copyMakeBorder(image, rows // 2, rows // 2, 0, 0, cv2.BORDER_CONSTANT)
        M = cv2.getPerspectiveTransform(pts1, pts2)
        return cv2.warpPerspective(padded_image, M, (cols, rows * 2))

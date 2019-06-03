import math
import time
from scipy import sparse
import numpy as np
from radon_server.radon_thread import RadonTransformThread


class TwoScaleTransform(RadonTransformThread):
    direct_radon_time = 0
    add_to_radon_time = 0
    merge_time = 0
    minSquareSize = 4

    def get_algorithm_name(self):
        return "twoscale"

    def run_algorithm(self, image, n, variant=None):
        self.run_two_scale_radon(image, n)

    # direct radon transform - used when we reached to a small image that can no longer calculated recursively
    def direct_radon(self, image, n):
        global direct_radon_time
        start = time.time()

        M = np.shape(image)[0]
        N = np.shape(image)[1]
        radon = np.zeros((n, n), dtype='float64')

        paddedImage = np.pad(image, 1, 'edge')
        min_r = -math.sqrt(2 * math.pow(n / 2, 2))
        max_r = math.sqrt(2 * math.pow(n / 2, 2))

        for h in range(0, n):
            # calculate radon for horizontal lines
            for k in range(0, n / 2):
                theta = math.pi * 0.25 + (k * math.pi) / (n - 2)

                r = min_r + (max_r - min_r) * h / (n - 1)
                x = np.array(range(int(-M / 2), int(M / 2)))
                y = (r - x * np.cos(theta)) / np.sin(theta)
                x += M / 2
                y += N / 2

                # calculate weights of line between pixels
                y1 = np.floor(y).astype(int)
                w1 = 1 - (y - y1)
                y2 = np.floor(y + 1).astype(int)
                w2 = (y - y1)

                # cut out of bounds values
                # lower bound
                x = x[np.where(y1 >= -1)]
                w1 = w1[np.where(y1 >= -1)]
                w2 = w2[np.where(y1 >= -1)]
                y2 = y2[np.where(y1 >= -1)]
                y1 = y1[np.where(y1 >= -1)]

                # upper bound
                x = x[np.where(y2 <= N)]
                w1 = w1[np.where(y2 <= N)]
                w2 = w2[np.where(y2 <= N)]
                y1 = y1[np.where(y2 <= N)]
                y2 = y2[np.where(y2 <= N)]

                radon[h, k] = ((paddedImage[x + 1, y1 + 1] * w1).sum() + (paddedImage[x + 1, y2 + 1] * w2).sum())

            # calculate radon for vertical lines
            for k in range(0, n / 2):
                theta = math.pi * 0.75 + (k * math.pi) / (n - 2)
                r = min_r + (max_r - min_r) * h / (n - 1)
                y = np.array(range(int(-N / 2), int(N / 2)))
                x = (r - y * np.sin(theta)) / np.cos(theta)
                x += N / 2
                y += M / 2

                # calculate weights of line between pixels
                x1 = np.floor(x).astype(int)
                w1 = 1 - (x - x1)
                x2 = np.floor(x + 1).astype(int)
                w2 = (x - x1)

                # cut out of bounds values
                # lower bound
                y = y[np.where(x1 >= -1)]
                w1 = w1[np.where(x1 >= -1)]
                w2 = w2[np.where(x1 >= -1)]
                x2 = x2[np.where(x1 >= -1)]
                x1 = x1[np.where(x1 >= -1)]

                # upper bound
                y = y[np.where(x2 <= N)]
                w1 = w1[np.where(x2 <= N)]
                w2 = w2[np.where(x2 <= N)]
                x1 = x1[np.where(x2 <= N)]
                x2 = x2[np.where(x2 <= N)]

                radon[h, n / 2 + k] = (
                        (paddedImage[x1 + 1, y + 1] * w1).sum() + (paddedImage[x2 + 1, y + 1] * w2).sum())

        duration = (time.time() - start) * 1000
        direct_radon_time += duration

        return radon

    def add_to_radon(self, radon, radonq, r, p, n, rfactors, pfactors, indexes):
        global add_to_radon_time

        start = time.time()
        pairs = np.transpose([np.reshape(r, n * n), np.reshape(np.tile(p, n), n * n)])  # 2s
        valid_pairs = np.where(
            (pairs[:, 0] >= 0) * (pairs[:, 0] <= n / 2) * (pairs[:, 1] >= 0) * (pairs[:, 1] <= n / 2))  # 1s
        values = np.transpose(pairs[valid_pairs])  # 0.5s
        pos = np.transpose(indexes[valid_pairs])  # 0.5s
        factors = np.transpose([np.reshape(rfactors, n * n), np.reshape(np.tile(pfactors, n), n * n)])  # 2s
        valid_factors = np.transpose(factors[valid_pairs])  # 0.5s
        radon[pos[0], pos[1]] += radonq[values[0], values[1]] * valid_factors[0] * valid_factors[1]  # 1.5s

        duration = (time.time() - start) * 1000
        self.add_to_radon_time += duration

    def merge_radon_squares(self, radon1, radon2, radon3, radon4, n):
        global merge_time

        start = time.time()

        min_r_q = -math.sqrt(2 * math.pow(n / 4, 2))
        max_r_q = math.sqrt(2 * math.pow(n / 4, 2))
        min_r = -math.sqrt(2 * math.pow(n / 2, 2))
        max_r = math.sqrt(2 * math.pow(n / 2, 2))
        min_phi = 0.25 * math.pi
        max_phi = 1.25 * math.pi
        radon = np.zeros((n, n), dtype="float64")
        radon1 = np.pad(radon1, 1, 'edge')[1:, 1:]
        radon2 = np.pad(radon2, 1, 'edge')[1:, 1:]
        radon3 = np.pad(radon3, 1, 'edge')[1:, 1:]
        radon4 = np.pad(radon4, 1, 'edge')[1:, 1:]

        j = np.arange(0, n)
        i = np.arange(0, n)
        phi = min_phi + (max_phi - min_phi) * i / (n - 1)
        phi = phi.reshape((n, 1))
        rs = min_r + (max_r - min_r) * j / (n - 1)
        r1 = rs + (n / 4) * np.cos(phi) + (n / 4) * np.sin(phi)
        r1_ind = ((r1 - min_r_q) / (max_r_q - min_r_q)) * (n / 2 - 1)
        r2 = rs + (n / 4) * np.cos(phi) - (n / 4) * np.sin(phi)
        r2_ind = ((r2 - min_r_q) / (max_r_q - min_r_q)) * (n / 2 - 1)
        r3 = rs - (n / 4) * np.cos(phi) + (n / 4) * np.sin(phi)
        r3_ind = ((r3 - min_r_q) / (max_r_q - min_r_q)) * (n / 2 - 1)
        r4 = rs - (n / 4) * np.cos(phi) - (n / 4) * np.sin(phi)
        r4_ind = ((r4 - min_r_q) / (max_r_q - min_r_q)) * (n / 2 - 1)

        # split each value into the 4 closest points
        r1_ind_low = np.floor(r1_ind).astype(int)
        r1_ind_high = np.floor(r1_ind + 1).astype(int)
        r1_ind_low_factor = 1 - (r1_ind - r1_ind_low)
        r1_ind_high_factor = 1 - (r1_ind_high - r1_ind)

        r2_ind_low = np.floor(r2_ind).astype(int)
        r2_ind_high = np.floor(r2_ind + 1).astype(int)
        r2_ind_low_factor = 1 - (r2_ind - r2_ind_low)
        r2_ind_high_factor = 1 - (r2_ind_high - r2_ind)

        r3_ind_low = np.floor(r3_ind).astype(int)
        r3_ind_high = np.floor(r3_ind + 1).astype(int)
        r3_ind_low_factor = 1 - (r3_ind - r3_ind_low)
        r3_ind_high_factor = 1 - (r3_ind_high - r3_ind)

        r4_ind_low = np.floor(r4_ind).astype(int)
        r4_ind_high = np.floor(r4_ind + 1).astype(int)
        r4_ind_low_factor = 1 - (r4_ind - r4_ind_low)
        r4_ind_high_factor = 1 - (r4_ind_high - r4_ind)

        phi_ind = ((phi - min_phi) / (max_phi - min_phi)) * (n / 2 - 1)
        ps_ind_low = np.floor(phi_ind).astype(int)
        ps_ind_high = np.floor(phi_ind).astype(int) + 1
        ps_ind_low_factor = 1 - (phi_ind - ps_ind_low)
        ps_ind_high_factor = 1 - (ps_ind_high - phi_ind)

        indexes = np.transpose([np.tile(np.arange(n), n), np.repeat(np.arange(n), n)])

        duration = (time.time() - start) * 1000
        self.merge_time += duration

        # add four points of top-left quarter
        self.add_to_radon(radon, radon1, r1_ind_low, ps_ind_low, n, r1_ind_low_factor, ps_ind_low_factor, indexes)
        self.add_to_radon(radon, radon1, r1_ind_low, ps_ind_high, n, r1_ind_low_factor, ps_ind_high_factor, indexes)
        self.add_to_radon(radon, radon1, r1_ind_high, ps_ind_low, n, r1_ind_high_factor, ps_ind_low_factor, indexes)
        self.add_to_radon(radon, radon1, r1_ind_high, ps_ind_high, n, r1_ind_high_factor, ps_ind_high_factor, indexes)

        # add four points of top-right quarter
        self.add_to_radon(radon, radon2, r2_ind_low, ps_ind_low, n, r2_ind_low_factor, ps_ind_low_factor, indexes)
        self.add_to_radon(radon, radon2, r2_ind_low, ps_ind_high, n, r2_ind_low_factor, ps_ind_high_factor, indexes)
        self.add_to_radon(radon, radon2, r2_ind_high, ps_ind_low, n, r2_ind_high_factor, ps_ind_low_factor, indexes)
        self.add_to_radon(radon, radon2, r2_ind_high, ps_ind_high, n, r2_ind_high_factor, ps_ind_high_factor, indexes)

        # add four points of bottom-left quarter
        self.add_to_radon(radon, radon3, r3_ind_low, ps_ind_low, n, r3_ind_low_factor, ps_ind_low_factor, indexes)
        self.add_to_radon(radon, radon3, r3_ind_low, ps_ind_high, n, r3_ind_low_factor, ps_ind_high_factor, indexes)
        self.add_to_radon(radon, radon3, r3_ind_high, ps_ind_low, n, r3_ind_high_factor, ps_ind_low_factor, indexes)
        self.add_to_radon(radon, radon3, r3_ind_high, ps_ind_high, n, r3_ind_high_factor, ps_ind_high_factor, indexes)

        # add four points of bottom-right quarter
        self.add_to_radon(radon, radon4, r4_ind_low, ps_ind_low, n, r4_ind_low_factor, ps_ind_low_factor, indexes)
        self.add_to_radon(radon, radon4, r4_ind_low, ps_ind_high, n, r4_ind_low_factor, ps_ind_high_factor, indexes)
        self.add_to_radon(radon, radon4, r4_ind_high, ps_ind_low, n, r4_ind_high_factor, ps_ind_low_factor, indexes)
        self.add_to_radon(radon, radon4, r4_ind_high, ps_ind_high, n, r4_ind_high_factor, ps_ind_high_factor, indexes)

        return radon

    # Direct implementation - using loops, slower but more readable
    def get_factorized_value(self, source, x, y, n):
        # split the value into the 4 closest points
        y_ind_low = int(math.floor(y))
        y_ind_high = int(math.floor(y + 1))
        y_ind_low_factor = 1 - (y - y_ind_low)
        y_ind_high_factor = 1 - (y_ind_high - y)

        x_ind_low = int(math.floor(x))
        x_ind_high = int(math.floor(x) + 1)
        x_ind_low_factor = 1 - (x - x_ind_low)
        x_ind_high_factor = 1 - (x_ind_high - x)

        value = 0
        if (x_ind_low >= 0 and y_ind_low >= 0 and x_ind_low <= n and y_ind_low <= n):
            value += source[x_ind_low, y_ind_low] * x_ind_low_factor * y_ind_low_factor
        if (x_ind_high >= 0 and y_ind_low >= 0 and x_ind_high <= n and y_ind_low <= n):
            value += source[x_ind_high, y_ind_low] * x_ind_high_factor * y_ind_low_factor
        if (x_ind_low >= 0 and y_ind_high >= 0 and x_ind_low <= n and y_ind_high <= n):
            value += source[x_ind_low, y_ind_high] * x_ind_low_factor * y_ind_high_factor
        if (x_ind_high >= 0 and y_ind_high >= 0 and x_ind_high <= n and y_ind_high <= n):
            value += source[x_ind_high, y_ind_high] * x_ind_high_factor * y_ind_high_factor

        return value

    def merge_radon_squares_loop(self, radon1, radon2, radon3, radon4, n):
        min_r_q = -math.sqrt(2 * math.pow(n / 4, 2))
        max_r_q = math.sqrt(2 * math.pow(n / 4, 2))
        min_r = -math.sqrt(2 * math.pow(n / 2, 2))
        max_r = math.sqrt(2 * math.pow(n / 2, 2))
        min_phi = 0.25 * math.pi
        max_phi = 1.25 * math.pi
        radon = np.zeros((n, n), dtype="float64")
        radon1 = np.pad(radon1, 1, 'edge')[1:, 1:]
        radon2 = np.pad(radon2, 1, 'edge')[1:, 1:]
        radon3 = np.pad(radon3, 1, 'edge')[1:, 1:]
        radon4 = np.pad(radon4, 1, 'edge')[1:, 1:]

        for i in range(0, n):
            phi = min_phi + (max_phi - min_phi) * i / (n - 1)
            for j in range(0, n):
                r = min_r + (max_r - min_r) * j / (n - 1)
                phi_q = float(phi)
                phi_ind = ((phi_q - min_phi) / (max_phi - min_phi)) * (n / 2 - 1)

                r1 = float(r) + (n / 4) * math.cos(phi) + (n / 4) * math.sin(phi)
                r1_ind = ((r1 - min_r_q) / (max_r_q - min_r_q)) * (n / 2 - 1)

                r2 = float(r) + (n / 4) * math.cos(phi) - (n / 4) * math.sin(phi)
                r2_ind = ((r2 - min_r_q) / (max_r_q - min_r_q)) * (n / 2 - 1)

                r3 = float(r) - (n / 4) * math.cos(phi) + (n / 4) * math.sin(phi)
                r3_ind = ((r3 - min_r_q) / (max_r_q - min_r_q)) * (n / 2 - 1)

                r4 = float(r) - (n / 4) * math.cos(phi) - (n / 4) * math.sin(phi)
                r4_ind = ((r4 - min_r_q) / (max_r_q - min_r_q)) * (n / 2 - 1)

                radon[j, i] += (self.get_factorized_value(radon1, r1_ind, phi_ind, n / 2) +
                                self.get_factorized_value(radon2, r2_ind, phi_ind, n / 2) +
                                self.get_factorized_value(radon3, r3_ind, phi_ind, n / 2) +
                                self.get_factorized_value(radon4, r4_ind, phi_ind, n / 2))

    # non recursive run (bottom-up)
    def run_two_scale_radon(self, image, n):
        # make the image an exponent of 2 size
        f = math.ceil(math.log(n, 2))
        new_n = int(math.pow(2, f))
        image = np.pad(image, (new_n - n)//2, 'constant')
        n = new_n
        self.radon = np.zeros((n, n), dtype='float64')

        # load radon 4x4 calculation matrix
        A = sparse.load_npz("radon_server/npz/direct_radon4x4.npz")

        # calculate direct radon transform for the minimum squares
        size = self.minSquareSize
        for x in np.arange(0, n, size):
            for y in np.arange(0, n, size):
                square = image[x:x + size, y:y + size]
                # calculate radon using matrix multiplication
                X = np.reshape(square, (self.minSquareSize * self.minSquareSize))
                R = A * X
                r = np.reshape(R, (self.minSquareSize, self.minSquareSize))
                self.radon[x:x + size, y:y + size] = r

        # calculate number of steps
        steps = 0
        while size <= n:
            size = size * 2
            steps += (n // size) * (n // size)

        size = self.minSquareSize
        step = 0
        # marge results until we get to nxn size
        while size < n:
            size = size * 2
            for x in np.arange(0, n, size):
                for y in np.arange(0, n, size):
                    radon1 = self.radon[x:x + size // 2, y:y + size // 2]
                    radon2 = self.radon[x:x + size // 2, y + size // 2:y + size]
                    radon3 = self.radon[x + size // 2:x + size, y:y + size // 2]
                    radon4 = self.radon[x + size // 2:x + size, y + size // 2:y + size]
                    r = self.merge_radon_squares(radon1, radon2, radon3, radon4, size)
                    self.radon[x:x + size, y:y + size] = r
                    self.update_progress(step, steps)
                    step += 1
        print("merge time:" + str(self.merge_time))
        print("add to radon time:" + str(self.add_to_radon_time))

    # recursive function - top-down
    def two_scale_radon(self, image, n, radon4x4Matrix):
        if n > self.minSquareSize:
            image1 = image[0:n // 2, 0:n // 2]
            image2 = image[0:n // 2, n // 2:n]
            image3 = image[n // 2:n, 0:n // 2]
            image4 = image[n // 2:n, n // 2:n]
            radon1 = self.two_scale_radon(image1, n // 2, radon4x4Matrix)
            radon2 = self.two_scale_radon(image2, n // 2, radon4x4Matrix)
            radon3 = self.two_scale_radon(image3, n // 2, radon4x4Matrix)
            radon4 = self.two_scale_radon(image4, n // 2, radon4x4Matrix)
            return self.merge_radon_squares(radon1, radon2, radon3, radon4, n)
        else:
            # calculate radon using matrix multiplication
            X = np.reshape(image, (self.minSquareSize * self.minSquareSize))
            R = radon4x4Matrix * X
            r = np.reshape(R, (self.minSquareSize, self.minSquareSize))
            # r = FSS(image, n)
            return r
            # return direct_radon(image, minSquareSize)

import numpy as np

from radon_server.radon_thread import RadonTransformThread


class FastSlantStackTransform(RadonTransformThread):
    def get_algorithm_name(self):
        return "fss"

    def run_algorithm(self, image, n, variant=None):
        self.fss(image, n)

    def ffft(self, x, alpha):
        # y=ffft(x,alpha)
        # fast algorithm for the fractional fft
        # inputs:
        # x - the input vector
        # alpha - the scaling coefficient
        # Ofer Levi - Jan 21 2012
        x = x[:]
        x = np.fft.fftshift(x)  # centering x indices arround zero
        n = len(x)
        E = 1j * np.pi * alpha / n
        ivec = np.transpose(np.arange(-(n / 2), (n / 2)))
        Dd = np.exp(-E * ivec * ivec)
        Dx = Dd * x  # multiplication with the appropriate diagonal matrix of complex exponnentials
        z = np.concatenate((Dx, np.zeros(n, dtype='float64')))  # zero padding
        ivec2 = (np.arange(0, n, dtype='float64')).transpose()
        T1stCol = np.exp(E * ivec2 * ivec2)  # 1st column of the Toeplitz matrix
        C1stCol = np.concatenate((T1stCol, [0], np.flipud(T1stCol[1:n])))  # 1st column of the circulant matrix

        D2d = np.fft.fft(C1stCol) / np.sqrt(n)  # applying normalyzed fft to the first column of C

        Fz = np.fft.fft(z)
        D2Fz = D2d * Fz  #
        Cz = np.fft.ifft(D2Fz)  # the convolution result of z and the 1st column of C (which is equivalent to C*z)

        TDx = Cz[0:n]  # ommiting the last n entries of Cz
        y = Dd * TDx  # Left multiflication with the appropriate diagonal matrix
        return y
        # written by Ofer Levi 18/4/2007

    def ffft2(self, x, alpha):
        m = len(x)
        n = 2 * m
        t = np.zeros(n, dtype='complex')
        y = np.zeros(n, dtype='complex')
        j = np.arange(0, m, dtype='float64')

        y[0:m] = x * np.exp(1j * np.pi * alpha * (j - j * j / m))

        t[0:m] = np.exp(-1j * np.pi * alpha / m * j * j)
        t[m + 1:2 * m] = np.flip(t[1:m], 0)

        t = np.fft.fft(np.conj(t))

        y = np.fft.fft(y) * t
        y = np.fft.ifft(y)

        y = y[0:m] * np.exp(1j * np.pi * alpha * (j - m / 2 - j * j / m))
        return y

    def ppfft(self, image):
        n = len(image)
        Y = np.zeros((2 * n, 2 * n), dtype='complex')

        # Basically Horizontal Lines
        PaddedX = np.concatenate((np.zeros((n // 2, n)), image, np.zeros((n // 2, n))))
        Z = np.fft.fftshift(PaddedX, 0)
        Z = np.fft.fft(Z, axis=0)
        Z = np.fft.fftshift(Z, 0)

        for r in range(0, n):
            alpha = float(n - r) / n
            t = self.ffft2(Z[r, :], alpha)
            Y[0:n, r] = t.transpose()
            alpha = float(-r) / n
            t = self.ffft2(Z[r + n, :], alpha)
            Y[0:n, r + n] = t.transpose()
            self.update_progress(r, n*3)

        PaddedX = np.hstack((np.zeros((n, n // 2)), image, np.zeros((n, n // 2)))).transpose()
        Z = np.fft.fftshift(PaddedX, 0)
        Z = np.fft.fft(Z, axis=0)
        Z = np.fft.fftshift(Z, 0)

        Z = np.vstack((Z[1:2 * n, :], Z[0, :]))  # Move left edge to right edge to include the right border edges
        for r in range(0, n):
            alpha = float(n - r) / n
            t = self.ffft2(Z[2 * n - r - 1, :], alpha)
            Y[n:2 * n, r] = t.transpose()
            alpha = float(-r) / n
            t = self.ffft2(Z[n - r - 1, :], alpha)
            Y[n:2 * n, r + n] = t.transpose()
            self.update_progress(n+r, n*3)

        Y = Y / (np.sqrt(2) * n)  # Normalization
        return Y

    def fss(self, image, n):
        self.radon = np.zeros((2 * n, 2 * n), dtype='float64')
        P = self.ppfft(image).transpose()
        P = np.fft.fftshift(P, axes=0)
        P = np.fft.ifft(P, axis=0)
        P = np.fft.fftshift(P, axes=0)
        S = np.real(P) * 2 * n
        self.radon = S
        self.update_progress(100,100)

    def Adj_PPFFT(self, Y):
        m = len(Y)
        n = int(m / 2)

        X0 = np.zeros((m, n), dtype='complex')
        X1 = np.zeros((m, n), dtype='complex')

        Y = Y * (np.sqrt(2) * n)

        Y0 = Y[0:n, :]
        Y1 = Y[n:m, :]

        for r in range(0, n):
            alpha = float(n - r) / n
            t = self.ffft2(Y0[:, r].transpose(), -alpha)
            X0[r, :] = t

            alpha = float(-r) / n
            t = self.ffft2(Y0[:, r + n].transpose(), -alpha)
            X0[r + n, :] = t

        X0 = np.fft.fftshift(X0, axes=0)
        X0 = np.fft.ifft(X0, axis=0)  # ,[],1)
        X0 = np.fft.fftshift(X0, axes=0)

        for r in range(0, n):
            alpha = float(n - r) / n
            t = self.ffft2(Y1[:, r].transpose(), -alpha)
            X1[m - r - 1, :] = t

            alpha = float(-r) / n
            t = self.ffft2(Y1[:, n + r].transpose(), -alpha)
            X1[n - r - 1, :] = t

        X1 = np.vstack((X1[m - 1, :].reshape((1, n)), X1[0:m - 1, :]))
        X1 = np.fft.fftshift(X1, axes=0)
        X1 = np.fft.ifft(X1, axis=0)  # ,[],1)
        X1 = np.fft.fftshift(X1, axes=0).transpose()
        X1 = X1[:, n / 2:3 * n / 2]
        X0 = X0[n / 2:3 * n / 2, :]
        X = (X0 + X1) / n

        return X

    def Adj_FSS(self, S, n):
        m = n * 2
        P = np.fft.fftshift(S, axes=0)
        P = np.fft.fft(P, axis=0)
        P = np.fft.fftshift(P, axes=0)
        X = np.real(self.Adj_PPFFT(P.transpose()))
        return X

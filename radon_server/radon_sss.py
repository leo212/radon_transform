import numpy as np

from radon_server.radon_thread import RadonTransformThread


class SlowSlantStackTransform(RadonTransformThread):
    def __init__(self, action="transform", variant=None, args=None):
        super(SlowSlantStackTransform, self).__init__(action, variant, args)
        self.ratio = 2

    def get_algorithm_name(self):
        return "sss"

    def run_transform(self, image, n, variant=None):
        self.slow_slant_stack(image, n)

    def slow_slant_stack(self, image, n):
        self.radon = np.zeros((n * 2, n * 2), dtype='float64')
        k = np.fft.fftshift(np.arange(-n, n))

        kn = (np.arange(0, n) - n // 2)

        # vertical lines
        rotatedImage = np.transpose(image)
        paddedImage = np.pad(rotatedImage, n // 2, mode='constant')[n // 2:n // 2 + n, :]
        fft_matrix = np.fft.fft(paddedImage)

        for s in range(n):
            p = (float(n-s) - n / 2) / float(n / 2)
            shiftby_arr = kn * p
            shifted_fft_matrix = fft_matrix * np.exp(-1j * 2 * np.pi * k * shiftby_arr.reshape(n, 1) / (n * 2))
            skewed = np.real(np.fft.ifft(shifted_fft_matrix)).astype('float64')
            self.radon[:, s] = sum(skewed)
            self.update_progress(s, n*2)

        paddedImage = np.pad(image, n // 2, mode='constant')[n // 2:n // 2 + n, :]
        fft_matrix = np.fft.fft(paddedImage)

        # horizontal lines
        for s in range(n):
            p = (float(s) - n / 2) / float(n / 2)
            shiftby_arr = kn * p
            shifted_fft_matrix = fft_matrix * np.exp(-1j * 2 * np.pi * k * shiftby_arr.reshape(n, 1) / (n * 2))
            skewed = np.fliplr(np.real(np.fft.ifft(shifted_fft_matrix)).astype('float64'))
            self.radon[:, s + n] = np.roll(sum(skewed), 1)
            self.update_progress(n+s, n*2)

        self.radon = self.radon / (np.sqrt(2) * n)  # Normalization
        self.radon = self.radon * 2 * n

import skimage
import numpy as np
from radon_server.radon_thread import RadonTransformThread


class PBIMTransform(RadonTransformThread):
    def get_algorithm_name(self):
        return "pbim"

    def run_transform(self, image, steps, variant=None):
        self.radon = np.zeros((steps, steps), dtype='float64')
        for s in range(steps):
            rotation = skimage.transform.rotate(image, -float(s) * 180 / steps).astype('float64')
            self.radon[:, s] = sum(rotation)
            self.update_progress(s, steps)
        return self.radon

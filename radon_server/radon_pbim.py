from scipy import misc
from radon_server.radon_thread import RadonTransformThread


class PBIMTransform(RadonTransformThread):
    def get_algorithm_name(self):
        return "pbim"

    def run_algorithm(self, image, steps):
        for s in range(steps):
            rotation = misc.imrotate(image, -float(s) * 180 / steps, interp="bilinear").astype('float64')
            self.radon[:, s] = sum(rotation)
            self.update_progress(s, steps)
        return self.radon

import numpy as np


class MathUtils:
    def __init__(self):
        pass

    def createColor(r, g, b):
        if (r <= 255 and g <= 255 and b <= 255):
            return [r / 255, g / 255, b / 255]
        else:
            raise Exception("Please input valid RGB values.")

    def Down():
        return np.array([0, -1.0, 0], dtype=np.float32)

    def __gaussian(self, x):
        return (x * x) + 0.5
        #return np.pow(np.e, -np.pow(x + 1, 2, dtype=np.float32), dtype=np.float32) + np.pow(np.e, -np.pow(x - 1, 2, dtype=np.float32), dtype=np.float32)

    def computeGaussianIntegral(self, lower, upper):
        lower_bound = self.__gaussian(lower)
        upper_bound = self.__gaussian(upper)

        rectangle = (np.min([upper_bound, lower_bound]) * (upper - lower))
        triangle = (np.abs(upper_bound - lower_bound) * (upper - lower) / 2)

        area = rectangle + triangle

        return int(area * 200)
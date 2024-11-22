import numpy as np
from enum import Enum
from src.utils import MathUtils

class PositionTypes:
    def __init__(self):
        pass

    def checkLength(self, array, length):
        if (len(array) == length):
            return array
        else:
            raise Exception("Please input a valid 3 dimensional array for the circle center.")

    def checkNumeric(self, array):
        if (np.issubdtype(array.dtype, np.float32)):
            return array
        else:
            raise Exception("Please input a valid array, containing only numbers.")
        
    def createArray(x, y, z):
        return np.array([x, y, z], dtype=np.float32)

class CirclePosition(PositionTypes):
    def __init__(self, center):
        self.center = super().checkNumeric(super().checkLength(center, 3))

class LinePosition(PositionTypes):
    def __init__(self, start, end):
        self.start = super().checkNumeric(super().checkLength(start, 3))
        self.end = super().checkNumeric(super().checkLength(end, 3))

class ArrowPosition(PositionTypes):
    def __init__(self, start, end):
        self.start = super().checkNumeric(super().checkLength(start, 3))
        self.end = super().checkNumeric(super().checkLength(end, 3))

class Colors(Enum):
    RED =           MathUtils.createColor(220, 0.0, 0.0)
    GREEN =         MathUtils.createColor(0.0, 220, 0.0)
    BLUE =          MathUtils.createColor(0.0, 0.0, 220)
    LIGHT_GREEN =   MathUtils.createColor(73, 230, 144)
    LIGHT_RED =     MathUtils.createColor(232, 82, 74)
    LIGHT_BLUE =    MathUtils.createColor(59, 159, 217)
    MAGENTA =       MathUtils.createColor(190, 36, 201)
    PINK =          MathUtils.createColor(240, 46, 172)
    TEAL =          MathUtils.createColor(64, 202, 207)
    YELLOW =        MathUtils.createColor(227, 222, 64)

    
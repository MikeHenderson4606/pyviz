from src.app import App
from src.Circle import Circle
from src.Triangle import Triangle
from src.Line import Line
from src.Arrow import Arrow
from src.objtypes import *
from src.objtypes import PositionTypes as pt
import numpy as np

def trigFunc(x):
    return np.cos(x) * np.sin(x) / np.arctan(x)

def logFunc(x):
    if (x > 0):
        return np.log2(x)
    else:
        return -100

def negLog(x):
    if (x > 0):
        return logFunc(-x)
    else:
        return -100

def basicFunc(x):
    return x * x

def test3D(x, y):
    return 0
    #return np.pow(np.e, -(x * x)) * np.pow(np.e, -(y * y))

if __name__ == "__main__":
    width = 1200
    height = 720

    app = App(width, height)

    arrow = Arrow([0, 0, 0], [0, 0, 0], Colors.LIGHT_BLUE.value, z_index=25)
    arrow2 = Arrow([0, 0, 0], [0, 0, 0], Colors.LIGHT_RED.value, z_index=25)

    arrow.animate(func=trigFunc, steps=500)
    arrow2.animate(func=basicFunc, steps=500)
    app.draw3DFunction(func=test3D, lower=-3, upper=3)

    app.moveCamera([-10, 3, 10], [0, 0, 0], animate=True)
    app.moveCamera([-10, 3, -10], [0, 0, 0], animate=True)
    app.moveCamera([10, 3, -10], [0, 0, 0], animate=True)
    app.moveCamera([10, 3, 10], [0, 0, 0], animate=True)

    app.createAxes(hash_thickness=3)
    app.addObject(arrow)
    app.addObject(arrow2)
    app.run()

from hmac import new
import Triangle
from app import App
from Circle import Circle
from Triangle import Triangle
from Line import Line
from Arrow import Arrow
from objtypes import *
from objtypes import PositionTypes as pt
import numpy as np
import objtypes

def trigFunc(x):
    return np.cos(x) * np.sin(x) / np.arctan(x)

def logFunc(x):
    return np.log2(x)

def negLog(x):
    return logFunc(-x)

def basicFunc(x):
    return x * x

if __name__ == "__main__":
    width = 1200
    height = 720

    app = App(width, height)

    arrowPositions = np.arange(0, (2 * np.pi) + (2 * np.pi / 10),  2 * np.pi / 10, dtype=np.float32)
    for i in range(len(arrowPositions)):
        for j in range(len(arrowPositions)):
            arrow = Arrow([2 * np.sin(i) * np.cos(j), 2 * np.sin(i) * np.sin(j), 2 * np.cos(i)], [3 * np.sin(i) * np.cos(j), 3 * np.sin(i) * np.sin(j), 3 * np.cos(i)], color=Colors.LIGHT_BLUE.value)
            app.addObject(arrow)

    app.moveCamera([0, 0.5, 10], [0, 0, 0], animate=False)

    # app.addObject(arrow)
    # app.addObject(arrow2)

    # app.createAxes(hash_thickness=3)
    app.run()

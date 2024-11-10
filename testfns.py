import Triangle
from app import App
from Circle import Circle
from Triangle import Triangle
from Line import Line
import numpy as np

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

    rect = Line([-5.0, 0.0, 0.0], [5.0, 0.0, 0.0], 10, 20)
    triangle = Triangle()

    logCircle = Circle(radius=0.8, hollow=False, z_index=10)              # Create a circle following some log function
    app.createFunctionAnimation(logCircle, logFunc, loop=False)           # Animate that path

    negLogCircle = Circle(radius=0.8, hollow=False, z_index=10)
    app.createFunctionAnimation(negLogCircle, negLog, loop=False)

    trigCircle = Circle(radius=0.8, hollow=False, z_index = 10)
    app.createFunctionAnimation(trigCircle, trigFunc, loop=False)

    #app.drawFunction(basicFunc)

    app.addObject(logCircle)
    app.addObject(negLogCircle)
    app.addObject(trigCircle)
    # app.addObject(triangle)

    app.createAxes(hash_thickness=3)
    app.run()

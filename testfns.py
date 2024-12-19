from src.Quad import Quad
from src.Simulation import Simulation
from src.app import App
from src.Circle import Circle
from src.Triangle import Triangle
from src.Line import Line
from src.Arrow import Arrow
from src.objtypes import *
from src.objtypes import PositionTypes as pt
from src.utils import MathUtils as mt
from src.utils import HashTable as ht
from fluidsimulation import FluidSimulation
from typing import List
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
    return np.sqrt(x)

def findDistance(x, y):
    return np.sqrt(np.pow(x, 2) + np.pow(y, 2))

def test3D(x, y):
    # r = findDistance(x, y)
    # return np.sin(x) / r
    return test3D2(x, y) - 3

def test3D2(x, y):
    return np.cos(x) * np.sin(y) + 3

class TestSimulation(Simulation):
    def __init__(self):
        super().__init__()
        self.arrows = []

    def Render(self):
        # Create grid of arrows
        lower = -10
        upper = 10
        steps = 25
        x_values = np.linspace(lower, upper, steps)
        y_values = np.linspace(lower, upper, steps)
        for x_val in x_values:
            for y_val in y_values:
                length = np.array([0.0, 0.5, 0.0], dtype=np.float32)
                start = np.array([x_val, 0, y_val], dtype=np.float32)
                arrow = Arrow(start, start + length)
                self.app.addObject(arrow)
                self.arrows.append(arrow)
    
    def Update(self):
        for arrow in self.arrows:
            position = arrow.start
            dist = np.sqrt(np.pow(position[0], 2) + np.pow(position[1], 2) + np.pow(position[2], 2))
            if (dist != 0):
                newPosition = ArrowPosition(arrow.start, pt.createArray(arrow.end[0], (np.sin(self.iteration / 10) + 1) / (dist * dist), arrow.end[2]))
            else:
                newPosition = ArrowPosition(arrow.start, pt.createArray(arrow.end[0], 0, arrow.end[2]))
            arrow.updatePosition(newPosition)
        self.iteration += 1


if __name__ == "__main__":
    width = 1200
    height = 720

    app = App(width, height)
    sim = FluidSimulation(width=2.4, height=2.4, smoothing_dist=0.4, mu=0.5, show_background=False, show_particles=True)
    # app.draw3DFunction(func=test3D, lower=-3.0, upper=3.0)

    # app.moveCamera([0, 3, 10], [0, 0, 0])
    app.addSimulation(sim)
    app.run()

from abc import abstractmethod
from OpenGL.GL import *
import numpy as np
import ctypes
from OpenGL.GL.shaders import compileProgram, compileShader
from OpenGL.GLU import *
from abc import ABC, abstractmethod

class VObject(ABC):

    def __init__(self):
        self.animation_steps = []                   # Holds the vertex info for animation
        self.currStep = 0                           # Keeps track of the current animation step
        self.steps = 0
        self.lines = []
        self.doesAnimate = False
        self.doneCycle = False

    @abstractmethod
    def createVertices(self):
        pass

    @abstractmethod
    def instantiateGLObjects(self):
        pass

    @abstractmethod
    def draw(self):
        pass

    @abstractmethod
    def createFunctionAnimation(self, func, lower_bound, upper_bound, steps, loop, draw):
        discontinuity_threshold = 100
        self.potential_discontinuities = []
        self.doesLoop = loop
        self.doesAnimate = True
        self.steps = steps
        self.drawFunc = draw

        interval = (upper_bound - lower_bound) / steps
        loopIndices = np.arange(start=lower_bound, stop=upper_bound, step=interval)
        for i in loopIndices:
            self.animation_steps.append([float(i), float(func(i)), 0.0])
            if abs(func(i) - func(i - interval)) > discontinuity_threshold:
                self.potential_discontinuities.append(i)
                
    @abstractmethod
    def updatePosition(self, newPosition):
        pass

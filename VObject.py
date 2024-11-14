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
    def updatePosition(self, newPosition):
        pass

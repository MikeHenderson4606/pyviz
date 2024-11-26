from OpenGL.GL import *
import numpy as np
import ctypes
from OpenGL.GL.shaders import compileProgram, compileShader
from OpenGL.GLU import *

from objtypes import Colors
from src.VObject import VObject

class Text(VObject):

    def __init__(self, text, color=Colors.WHITE.value):
        self.text = text
        self.color = color

    def createVertices(self):
        return super().createVertices()
    
    def instantiateGLObjects(self):
        return super().instantiateGLObjects()
    
    def draw(self):
        return super().draw()
    
    def updatePosition(self):
        return super().updatePosition()
    
    def animate(self, animateTo, func, steps):
        return super().animate(animateTo, func, steps)
    
    def createAnimationPositions(self):
        return super().createAnimationPositions()
    
    def destroy(self):
        # Destroy vao and vbo
        glDeleteBuffers(0, (self.vbo,))
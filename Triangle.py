from OpenGL.GL import *
import numpy as np
import ctypes
from OpenGL.GL.shaders import compileProgram, compileShader
from OpenGL.GLU import *

from VObject import VObject

class Triangle(VObject):

    def __init__(self):
        super().__init__()
        self.z_index = 0
    
    def createVertices(self):
        print("Generating triangle vertices")
        # Initialize x, y, z, r, g, b values
        self.vertices = (
            -2.0, -2.0, 1.0, 1.0, 0.0, 0.0,
            2.0, -2.0, 1.0, 0.0, 1.0, 0.0,
            0.0, 2.0, 1.0, 0.0, 0.0, 1.0
        )
        self.vertices = np.array(self.vertices, dtype=np.float32)

        self.vertex_count = 3

    def instantiateGLObjects(self):
        # Create a vertex array object (vao)
        self.vao = glGenVertexArrays(1)
        glBindVertexArray(self.vao)

        # Create a vertex buffer object (vbo)
        self.vbo = glGenBuffers(1)
        glBindBuffer(GL_ARRAY_BUFFER, self.vbo)
        glBufferData(GL_ARRAY_BUFFER, self.vertices.nbytes, self.vertices, GL_STATIC_DRAW)

        # Tell OpenGL how to interpret the vertex data
        glEnableVertexAttribArray(0)
        glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, 24, ctypes.c_void_p(0))
        glEnableVertexAttribArray(1)
        glVertexAttribPointer(1, 3, GL_FLOAT, GL_FALSE, 24, ctypes.c_void_p(12))

    def draw(self):
        # Draw the triangle
        glBindVertexArray(self.vao)
        glDrawArrays(GL_TRIANGLES, 0, self.vertex_count)
        glBindVertexArray(0)

    def updatePosition(self, newPosition):
        return super().updatePosition(newPosition)

    def destroy(self):
        # Destroy vao and vbo
        glDeleteBuffers(0, (self.vbo,))
        glDeleteVertexArrays(0, (self.vao,))

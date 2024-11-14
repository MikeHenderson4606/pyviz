from OpenGL.GL import *
import numpy as np
import ctypes
from OpenGL.GL.shaders import compileProgram, compileShader
from OpenGL.GLU import *

from VObject import VObject

class Circle(VObject):

    def __init__(self, radius, hollow, z_index = 0, center = (0.0, 0.0, 0.0)):
        super().__init__()

        SCALING_FACTOR = 1 / 10
        self.center = center                        # The center of the circle (x, y, z)
        self.radius = radius / 10                   # Radius of circle
        self.CIRCLE_QUALITY = 500                   # int(500 * SCALING_FACTOR) # How many points the circle has
        self.hollow = hollow                        # If the circle is hollow or not
        self.z_index = z_index

    def createVertices(self):
        vertices = []

        if (self.hollow):
            for i in range(self.CIRCLE_QUALITY):
                angle = i / self.CIRCLE_QUALITY * (2 * np.pi)
                x = np.cos(angle) * self.radius + self.center[0]
                y = np.sin(angle) * self.radius + self.center[1]
                z = 0.0
                r = 1.0
                g = 0.0
                b = 0.0
                vertices.append([x, y, z, r, g, b])

            self.vertices = np.array(vertices, dtype=np.float32)
            self.vertex_count = int(len(vertices) / 6)
        else:
            vertices.append([*self.center, 1.0, 0.0, 0.0]) # Center point of the circle

            for i in range(self.CIRCLE_QUALITY + 1): # Add one to close the circle
                angle = i / self.CIRCLE_QUALITY * (2 * np.pi)
                x = np.cos(angle) * self.radius + self.center[0]
                y = np.sin(angle) * self.radius + self.center[1]
                z = 0.0
                r = 1.0
                g = 0.0
                b = 0.0
                vertices.append([x, y, z, r, g, b])

            self.vertices = np.array(vertices, dtype=np.float32)
            self.vertex_count = int(len(vertices) / 6)

    def instantiateGLObjects(self):
        # Create a vertex array object (vao)
        self.vao = glGenVertexArrays(1)
        glBindVertexArray(self.vao)

        # Create a vertex buffer object (vbo)
        self.vbo = glGenBuffers(1)
        flat_vertices = self.vertices.flatten()
        glBindBuffer(GL_ARRAY_BUFFER, self.vbo)
        glBufferData(GL_ARRAY_BUFFER, flat_vertices.nbytes, flat_vertices, GL_DYNAMIC_DRAW)

        # Tell OpenGL how to interpret the vertex data
        glEnableVertexAttribArray(0)
        glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, 24, ctypes.c_void_p(0))
        glEnableVertexAttribArray(1)
        glVertexAttribPointer(1, 3, GL_FLOAT, GL_FALSE, 24, ctypes.c_void_p(12))

    def draw(self):
        # Rebind partial buffer data in case of any updated vertices
        glBindBuffer(GL_ARRAY_BUFFER, self.vbo)
        flat_vertices = self.vertices.flatten()
        glBufferSubData(GL_ARRAY_BUFFER, 0, flat_vertices.nbytes, flat_vertices)
        
        # Draw the Circle
        glBindVertexArray(self.vao)
        if (self.hollow):
            glDrawArrays(GL_LINE_LOOP, 0, self.CIRCLE_QUALITY)
        else:
            glDrawArrays(GL_TRIANGLE_FAN, 0, self.CIRCLE_QUALITY + 2)
        glBindVertexArray(0)

    def updatePosition(self, newPosition):
        self.center = newPosition
        self.createVertices()

    def destroy(self):
        # Destroy vao and vbo
        glDeleteVertexArrays(0, (self.vao,))
        glDeleteBuffers(0, (self.vbo,))

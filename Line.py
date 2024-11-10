from OpenGL.GL import *
import numpy as np
import ctypes
from OpenGL.GL.shaders import compileProgram, compileShader
from OpenGL.GLU import *

from VObject import VObject

class Line(VObject):

    def __init__(self, start, end, z_index = 0, thickness = 1.0, color = (1.0, 1.0, 1.0)):
        super().__init__()

        self.start = start                          # The starting position of the line (x, y, z) as a list
        self.end = end                              # The ending position of the line (x, y, z) as a list
        self.thickness = thickness / 100            # Thickness of the line -- OpenGL depreciated line thickness past 1.0, so need to create a quad to visualize thicker lines
        self.color = color                          # Color
        self.z_index = z_index

    def createVertices(self):
        # Find the perpendicular vector
        dx = self.end[0] - self.start[0]
        dy = self.end[1] - self.start[1]
        dz = self.end[2] - self.start[2]
        # Normalize to ensure unit length
        length = np.sqrt(dx * dx + dy * dy + dz * dz)
        dx /= length
        dy /= length
        dz /= length

        # Introduce the thickness
        offset_x = -dy * self.thickness / 2.0   # Scaled perpendicular vector
        offset_y = dx * self.thickness / 2.0    # Scaled perpendicular vector
        offset_z = dz * self.thickness / 2.0    # Scaled perpendicular vector

        normals_1 = [[self.start[0] + offset_x, self.start[1] + offset_y, self.start[2] + offset_z], [self.start[0] - offset_x, self.start[1] - offset_y, self.start[2] - offset_z]]
        normals_2 = [[self.end[0] + offset_x, self.end[1] + offset_y, self.end[2] + offset_z], [self.end[0] - offset_x, self.end[1] - offset_y, self.end[2] - offset_z]]

        # Add color data      z    r    g    b
        normals_1[0].extend([0.0, self.color[0], self.color[1], self.color[2]])
        normals_1[1].extend([0.0, self.color[0], self.color[1], self.color[2]])
        normals_2[0].extend([0.0, self.color[0], self.color[1], self.color[2]])
        normals_2[1].extend([0.0, self.color[0], self.color[1], self.color[2]])

        # Create a list with the two endpoints
        vertices = [normals_1[0], normals_1[1], normals_2[0], normals_2[1]]
        self.vertices = np.array(vertices, dtype=np.float32)
        
    def instantiateGLObjects(self):
        # Create a vertex array object (vao)
        self.vao = glGenVertexArrays(1)
        glBindVertexArray(self.vao)

        # Create a vertex buffer object (vbo)
        self.vbo = glGenBuffers(1)
        flat_vertices = self.vertices.flatten()
        glBindBuffer(GL_ARRAY_BUFFER, self.vbo)
        glBufferData(GL_ARRAY_BUFFER, flat_vertices.nbytes, flat_vertices, GL_DYNAMIC_DRAW)

        # Specify indices
        self.indices = np.array([
            0, 1, 2, # First triangle
            2, 1, 3  # Second triangle
        ], dtype=np.uint32)
        
        # Create an element buffer object (ebo)
        self.ebo = glGenBuffers(1)
        glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, self.ebo)
        glBufferData(GL_ELEMENT_ARRAY_BUFFER, self.indices.nbytes, self.indices, GL_DYNAMIC_DRAW)

        # Tell OpenGL how to interpret the vertex/color data
        glEnableVertexAttribArray(0)
        glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, 24, ctypes.c_void_p(0))
        glEnableVertexAttribArray(1)
        glVertexAttribPointer(1, 3, GL_FLOAT, GL_FALSE, 24, ctypes.c_void_p(12))
    
    def draw(self):
        # Bind the vao
        glBindVertexArray(self.vao)
        # Rebind partial buffer data in case of any updated vertices
        glBindBuffer(GL_ARRAY_BUFFER, self.vbo)
        flat_vertices = self.vertices.flatten()
        glBufferSubData(GL_ARRAY_BUFFER, 0, flat_vertices.nbytes, flat_vertices)

        # Draw the Line
        glDrawElements(GL_TRIANGLES, 6, GL_UNSIGNED_INT, None)
        glBindVertexArray(0)

    def createFunctionAnimation(self, func, lower_bound, upper_bound, steps, loop, draw=True):
        return super().createFunctionAnimation(func, lower_bound, upper_bound, steps, loop, draw)

    def updatePosition(self, newPosition):
        return super().updatePosition(newPosition)

    def destroy(self):
        # Destroy vao and vbo
        glDeleteBuffers(0, (self.vbo,))
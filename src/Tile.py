from OpenGL.GL import *
import numpy as np
import ctypes
from OpenGL.GL.shaders import compileProgram, compileShader
from OpenGL.GLU import *

from src.VObject import VObject

class Tile(VObject):
    
    def __init__(self, vertices, z_index = 0, thickness = 1.0, color = (1.0, 1.0, 1.0)):
        super().__init__()
        self.vertices = vertices
        self.thickness = thickness / 100            # Thickness of the line -- OpenGL depreciated line thickness past 1.0, so need to create a quad to visualize thicker lines
        self.color = color                          # Color
        self.z_index = z_index

        if (len(vertices) == 4 and type(vertices) == np.ndarray):                # The starting position of the line (x, y, z) as a list
            self.createVertices()
        else:
            raise Exception("Vertices must include an array of length 4 with each element having length 3.")

    def createVertices(self):
        vertices = []
        for vertex in self.vertices:
            curr_vertex = [vertex[0], vertex[1], vertex[2], self.color[0], self.color[1], self.color[2]]
            vertices.append(curr_vertex)
        
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

        # Specify indices - draw both sides
        self.indices = np.array([
            0, 1, 2, # First triangle
            2, 1, 0, # Inverted first triangle
            2, 1, 3, # Second triangle
            3, 1, 2  # Inverted second triangle
        ], dtype=np.uint32)
        
        # Create an element buffer object (ebo)
        self.ebo = glGenBuffers(1)
        glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, self.ebo)
        glBufferData(GL_ELEMENT_ARRAY_BUFFER, self.indices.nbytes, self.indices, GL_DYNAMIC_DRAW)

        # Tell OpenGL how to interpret the vertex/color data
        glEnableVertexAttribArray(0)
        glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, 24, ctypes.c_void_p(0))
        # Color data
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
        glDrawElements(GL_TRIANGLES, 12, GL_UNSIGNED_INT, None)
        # Unbind VAO
        glBindVertexArray(0)
        
    def updatePosition(self, newPosition=None):
        return super().updatePosition(newPosition)
    
    def updateColor(self, newColor):
        self.color = newColor
        self.createVertices()

    def animate(self, animateTo):
        return super().animate(animateTo)
    
    def createAnimationPositions(self, newPosition):
        return super().createAnimationPositions(newPosition)

    def destroy(self):
        # Destroy vao and vbo
        glDeleteBuffers(0, (self.vbo,))
from email.policy import default
from OpenGL.GL import *
import numpy as np
import ctypes
from OpenGL.GL.shaders import compileProgram, compileShader
from OpenGL.GLU import *

from src.objtypes import LinePosition
from src.VObject import VObject

class Quad(VObject):

    def __init__(self, vertices, z_index = 0, thickness = 1.0, color = (1.0, 1.0, 1.0)):
        super().__init__()

        if (len(vertices) == 4):                # The starting position of the line (x, y, z) as a list
            self.vertices = []
            normal = np.cross(vertices[1] - vertices[0], vertices[2] - vertices[1])
            for vertex in vertices:
                self.vertices.append(np.append(vertex, np.array([
                    normal[0], normal[1], normal[2],
                    color[0], color[1], color[2]
                    ], dtype=np.float32)))

            self.vertices = np.array(self.vertices, dtype=np.float32)
        else:
            raise Exception("Start position must be a three dimensional vector")
        
        self.thickness = thickness / 100            # Thickness of the line -- OpenGL depreciated line thickness past 1.0, so need to create a quad to visualize thicker lines
        self.color = color                          # Color
        self.z_index = z_index

    def createVertices(self):
        pass
        
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
        glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, 36, ctypes.c_void_p(0))
        # Introduce normals
        glEnableVertexAttribArray(1)
        glVertexAttribPointer(1, 3, GL_FLOAT, GL_FALSE, 36, ctypes.c_void_p(12))
        # Color data
        glEnableVertexAttribArray(2)
        glVertexAttribPointer(2, 3, GL_FLOAT, GL_FALSE, 36, ctypes.c_void_p(24))

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
        
    def updatePosition(self):
        return super().updatePosition()
    
    def animate(self, animateTo):
        return super().animate(animateTo)
    
    def createAnimationPositions(self):
        return super().createAnimationPositions()

    def destroy(self):
        # Destroy vao and vbo
        glDeleteBuffers(0, (self.vbo,))

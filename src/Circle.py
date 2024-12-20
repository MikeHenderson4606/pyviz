from OpenGL.GL import *
import numpy as np
import ctypes
from OpenGL.GL.shaders import compileProgram, compileShader
from OpenGL.GLU import *

from src.objtypes import CirclePosition
from src.VObject import VObject

class Circle(VObject):

    def __init__(self, radius, hollow=False, z_index = 0, center = (0.0, 0.0, 0.0)):
        super().__init__()

        SCALING_FACTOR = 1 / 10
        self.center = center                        # The center of the circle (x, y, z)
        self.radius = radius / 10                   # Radius of circle
        self.CIRCLE_QUALITY = 25                   # int(500 * SCALING_FACTOR) # How many points the circle has
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

    def updatePosition(self, newPosition=None):
        if (isinstance(newPosition, CirclePosition)):
            self.center = newPosition.center
            self.createVertices()
        if (self.curr_step < len(self.animation_steps)):
            self.center = np.array([self.animation_steps[self.curr_step][0], self.animation_steps[self.curr_step][1], 0.0], dtype=np.float32)
            self.curr_step += 1
            self.createVertices()

    def animate(self, animateTo, func=None, steps=100):
        self.anim_func = func
        if (type(animateTo) == CirclePosition):
            self.animationPosition = animateTo
            self.createAnimationPositions(steps)
        else:
            raise Exception("Please input a valid coordinate to animate to.")

    def createAnimationPositions(self, steps):
        diff = self.animationPosition.center - self.center
        anim_x_values = []
        anim_y_values = []
        if (self.anim_func):
            x_values = np.arange(-10, 10, 20 / steps, dtype=np.float32)
            for x_val in x_values:
                anim_x_values.append(x_val)
                anim_y_values.append(self.anim_func(x_val))
        else:
            # Animate linearly along the path
            anim_x_values = np.arange(self.center, self.animationPosition + (diff[0] / steps), diff[0] / (steps - 1), dtype=np.float32)
            anim_y_values = np.arange(self.center, self.animationPosition + (diff[1] / steps), diff[1] / (steps - 1), dtype=np.float32)
    
        for i in range(steps):
            self.animation_steps.append([anim_x_values[i], anim_y_values[i], 0.0])

    def destroy(self):
        # Destroy vao and vbo
        glDeleteVertexArrays(0, (self.vao,))
        glDeleteBuffers(0, (self.vbo,))

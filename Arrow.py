
from OpenGL.GL import *
import numpy as np
import ctypes
from OpenGL.GL.shaders import compileProgram, compileShader
from OpenGL.GLU import *
from VObject import VObject
from objtypes import ArrowPosition

class Arrow(VObject):

    def __init__(self, start, end, color, thickness=5.0, z_index=0):
        super().__init__()
        if (len(start) == 3):
            self.start = np.array(start, dtype=np.float32)      # The starting position of the line (x, y, z) as a list
        else:
            raise Exception("Start position must be a three dimensional vector")
        if (len(end) == 3):
            self.end = np.array(end, dtype=np.float32)          # The ending position of the line (x, y, z) as a list
        else:
            raise Exception("End position must be a three dimentional vector")
        
        self.thickness = thickness / 100
        self.z_index = z_index
        self.color = color

    def __createRodVertices(self):
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
        offset_x = (-dy + dz) * self.thickness / 2.0   # Scaled perpendicular vector
        offset_y = dx * self.thickness / 2.0    # Scaled perpendicular vector
        offset_z = dz * self.thickness / 2.0   # Scaled perpendicular vector

        normals_1 = [[self.start[0] + offset_x, self.start[1] + offset_y, self.start[2] + offset_z], [self.start[0] - offset_x, self.start[1] - offset_y, self.start[2] - offset_z]]
        normals_2 = [[self.end[0] + offset_x, self.end[1] + offset_y, self.end[2] + offset_z], [self.end[0] - offset_x, self.end[1] - offset_y, self.end[2] - offset_z]]

        # Add color data      r            g                b
        normals_1[0].extend([self.color[0], self.color[1], self.color[2]])
        normals_1[1].extend([self.color[0], self.color[1], self.color[2]])
        normals_2[0].extend([self.color[0], self.color[1], self.color[2]])
        normals_2[1].extend([self.color[0], self.color[1], self.color[2]])

        # Create a list with the two endpoints
        vertices = [normals_1[0], normals_1[1], normals_2[0], normals_2[1]]
        return np.array(vertices, dtype=np.float32)

    def __createHeadVertices(self):
        scale = 0.13
        diff = self.end - self.start
        length = np.linalg.norm(diff)
        unit_vector = diff / length
        perp_unit_vector = np.array([-unit_vector[1], unit_vector[0], 0.0], dtype=np.float32)

        head_points = np.array([(self.end + (perp_unit_vector * scale)) - (unit_vector * scale), (self.end - (perp_unit_vector * scale)) - (unit_vector * scale)], dtype=np.float32)
        # Add color properties
        vertex1 = np.array(np.append(head_points[0], [self.color[0], self.color[1], self.color[2]]), dtype=np.float32)
        vertex2 = np.array(np.append(head_points[1], [self.color[0], self.color[1], self.color[2]]), dtype=np.float32)
        vertex3 = np.array(np.append(self.end + (unit_vector * scale), [self.color[0], self.color[1], self.color[2]]), dtype=np.float32)
        # Triangle has the points of the 2 generated vertices and the end vertex
        return np.array([vertex1, vertex2, vertex3], dtype=np.float32)

    def createVertices(self):
        rod_vertices = self.__createRodVertices()
        head_vertices = self.__createHeadVertices()

        self.vertices = np.append(rod_vertices, head_vertices)
    
    def instantiateGLObjects(self):
        # Create a vertex array object (vao)
        self.vao = glGenVertexArrays(1)
        glBindVertexArray(self.vao)

        # Create a vertex buffer object (vbo)
        self.vbo = glGenBuffers(1)
        flat_vertices = self.vertices.flatten()
        glBindBuffer(GL_ARRAY_BUFFER, self.vbo)
        glBufferData(GL_ARRAY_BUFFER, flat_vertices.nbytes, flat_vertices, GL_DYNAMIC_DRAW)

        # Specify indices - draw both sides so nothing goes out of view
        self.indices = np.array([
            0, 1, 2,        # First triangle - rod
            2, 1, 0,        # Inverted first triangle
            2, 1, 3,        # Second triangle - rod
            3, 1, 2,        # Inverted second triangle
            4, 5, 6,        # Third triangle - head
            6, 5, 4         # Inverted third triangle
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
        glDrawElements(GL_TRIANGLES, 18, GL_UNSIGNED_INT, None)
        glBindVertexArray(0)
    
    def updatePosition(self):
        # Iterate through animation positions
        if (self.curr_step < len(self.animation_steps)):
            self.start = np.array(self.animation_steps[self.curr_step][0], dtype=np.float32)
            self.end = np.array(self.animation_steps[self.curr_step][1], dtype=np.float32)
            self.curr_step += 1

        # Update vertex data
        self.createVertices()

    def animate(self, animateTo=ArrowPosition(np.array([0, 0, 0], dtype=np.float32), np.array([0, 0, 0], dtype=np.float32)), func=None, steps=100):
        if (type(animateTo) == ArrowPosition):
            self.anim_func = func
            self.animationPosition = animateTo
            self.createAnimationPositions(steps)
        else:
            raise Exception("Please input a valid coordinate to animate to.")

    def createAnimationPositions(self, steps):
        startDiff = self.animationPosition.start - self.start
        endDiff = self.animationPosition.end - self.end
        anim_start_x_values = []
        anim_start_y_values = []
        anim_start_z_values = []
        anim_end_x_values = []
        anim_end_y_values = []
        anim_end_z_values = []
    
        if (self.anim_func):
            # Animate along some specified function
            x_values = np.arange(-10, 10, 20 / steps, dtype=np.float32)
            for x_val in x_values:
                end_x_val = x_val + ((20 / steps) * 15)

                anim_start_x_values.append(x_val)
                anim_start_y_values.append(self.anim_func(x_val))
                anim_start_z_values.append(0)
                anim_end_x_values.append(end_x_val)
                anim_end_y_values.append(self.anim_func(end_x_val))
                anim_end_z_values.append(0)
        else:
            # Animate linearly along the path
            anim_start_x_values = [self.start[0]] * steps if startDiff[0] == 0 else np.arange(self.start[0], self.animationPosition.start[0] + (startDiff[0] / steps), startDiff[0] / (steps - 1), dtype=np.float32)
            anim_start_y_values = [self.start[1]] * steps if startDiff[1] == 0 else np.arange(self.start[1], self.animationPosition.start[1] + (startDiff[1] / steps), startDiff[1] / (steps - 1), dtype=np.float32)
            anim_start_z_values = [self.start[2]] * steps if startDiff[2] == 0 else np.arange(self.start[2], self.animationPosition.start[2] + (startDiff[2] / steps), startDiff[2] / (steps - 1), dtype=np.float32)
            anim_end_x_values = [self.end[0]] * steps if endDiff[0] == 0 else np.arange(self.end[0], self.animationPosition.end[0] + (endDiff[0] / steps), endDiff[0] / (steps - 1), dtype=np.float32)
            anim_end_y_values = [self.end[1]] * steps if endDiff[1] == 0 else np.arange(self.end[1], self.animationPosition.end[1] + (endDiff[1] / steps), endDiff[1] / (steps - 1), dtype=np.float32)
            anim_end_z_values = [self.end[2]] * steps if endDiff[2] == 0 else np.arange(self.end[2], self.animationPosition.end[2] + (endDiff[2] / steps), endDiff[2] / (steps - 1), dtype=np.float32)

        for i in range(steps):
            self.animation_steps.append(
                [[anim_start_x_values[i], anim_start_y_values[i], anim_start_z_values[i]], 
                [anim_end_x_values[i], anim_end_y_values[i], anim_end_z_values[i]]]
            )
    
    def destroy(self):
        # Destroy vao and vbo
        glDeleteBuffers(0, (self.vbo,))
    
    
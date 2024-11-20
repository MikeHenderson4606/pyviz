import pygame as pg
from OpenGL.GL import *
import numpy as np
import ctypes
from OpenGL.GL.shaders import compileProgram, compileShader
from OpenGL.GLU import *
from abc import ABC, abstractmethod
import pyrr

from GLUtils import GLUtils
from Animations import Animations
from Line import Line
from Circle import Circle
from Triangle import Triangle
from Quad import Quad
from Camera import Camera
from VObject import VObject
from utils import MathUtils

class App:

    def __init__(self, width, height):
        # Instantiate Application
        self.objects = []
        self.steps = 350
        self.clock = pg.time.Clock()

        # Generate initial view matrix camera coords
        self.camera = Camera()

        # Create animation class
        self.animator = Animations()

        # Create OpenGL utils class
        self.GLUtils = GLUtils(width, height, self.camera)

        # Create utils class
        self.utils = MathUtils()

    def createAxes(self, hash_length=0.12, hash_thickness=1, x_min = -10, x_max = 10, y_min = -10, y_max = 10, z_min=-10, z_max=10):
        x_axis = Line([x_min, 0.0, 0.0], [x_max, 0.0, 0.0], thickness=3)
        y_axis = Line([0.0, y_min, 0.0], [0.0, y_max, 0.0], thickness=3)
        z_axis = Line([0.0, 0.0, z_min], [0.0, 0.0, z_max], thickness=3)
        for i in range(int(x_max - x_min)):
            x_interval = i
            x_hash = Line([x_min + x_interval, hash_length / 2, 0.0], [x_min + x_interval, -hash_length / 2, 0.0], thickness=hash_thickness)
            self.addObject(x_hash)
            
        for i in range(int(y_max - y_min)):
            y_interval = i
            y_hash = Line([hash_length / 2, y_min + y_interval, 0.0], [-hash_length / 2, y_min + y_interval, 0.0], thickness=hash_thickness)
            self.addObject(y_hash)

        for i in range(int(z_max - z_min)):
            z_interval = i
            z_hash = Line([hash_length / 2, 0.0, z_min + z_interval], [-hash_length / 2, 0.0, z_min + z_interval], thickness=hash_thickness)
            self.addObject(z_hash)
        
        self.addObject(x_axis)
        self.addObject(y_axis)
        self.addObject(z_axis)

    def addObject(self, obj):
        if (isinstance(obj, VObject)):
            self.objects.append(obj)
            # Creating vertices
            obj.createVertices()
            # Instantiating objects
            obj.instantiateGLObjects()
            # Check for errors
            # self._checkGLErrors()
            # Sort the object back into the list of objects
            self.calculatePriorities()

    def removeObjects(self, objs):
        for obj in objs:
            self.objects.remove(obj)

    def drawFunction(self, func, lower, upper, steps=100):
        di = (lower - upper) / steps
        x_values = np.linspace(lower, upper, steps)
        for i in x_values:
            try:
                line = Line([i, func(i), 0.0], [i + di, func(i + di), 0.0], color=(0, 0, 0), thickness=2, z_index = 1)
                self.addObject(line)
            except:
                print("Out of range.")
                pass

    def draw3DFunction(self, func, lower, upper, steps=30):
        di = (upper - lower) / (steps - 1)
        x_values = np.linspace(lower, upper, steps)
        y_values = np.linspace(lower, upper, steps)
        for x_val in x_values:
            for y_val in y_values:
                value = func(x_val, y_val)                  # The function at the given index
                adj_x = func(x_val + di, y_val)             # The function evaluated slightly more along the x axis
                adj_y = func(x_val, y_val + di)             # The function evaluated slightly more along the y axis
                adj_both = func(x_val + di, y_val + di)     # The function evaluated slightly more along both axes
                vertices = np.array([
                    [x_val, value, y_val],
                    [x_val + di, adj_x, y_val],
                    [x_val, adj_y, y_val + di,],
                    [x_val + di, adj_both, y_val + di],
                ], dtype=np.float32)
                quad = Quad(vertices=vertices)
                self.addObject(quad)

    def drawObjects(self):
        for obj in self.objects:
            obj.updatePosition()
            if (isinstance(obj, Quad)):
                self.GLUtils.setTranslucentShader()
                obj.draw()
            else:
                self.GLUtils.setDefaultShader()
                obj.draw()

    def moveCamera(self, pos, focus, animate=False):
        if (animate):
            self.camera.generateCameraPositions(pos, focus)
        else:
            self.camera.moveCamera(pos, focus)
            self.GLUtils.initMatrices()

    def animateCamera(self):
        if (self.camera.curr_step < len(self.camera.camera_animation)):
            self.camera.moveCamera(self.camera.camera_animation[self.camera.curr_step], self.camera.camera_focus)
            self.camera.incrementStep()

    def calculatePriorities(self):
        def z_indexSort(obj):
            return obj.z_index
        
        self.objects.sort(reverse=True, key=z_indexSort)

    def run(self):
        running = True
        while (running):
            for event in pg.event.get():
                if (event.type == pg.QUIT):
                    running = False
                if (event.type == pg.KEYDOWN):
                    if (event.key == pg.K_ESCAPE):
                        running = False
                    if (event.key == pg.K_d):
                        self.camera.moveCameraBy(np.array([1.0, 0.0, 0.0], dtype=np.float32))    
                    if (event.key == pg.K_a):
                        self.camera.moveCameraBy(np.array([-1.0, 0.0, 0.0], dtype=np.float32))
                    if (event.key == pg.K_w):
                        self.camera.moveCameraBy(np.array([0.0, 0.0, -1.0], dtype=np.float32))  
                    if (event.key == pg.K_s):
                        self.camera.moveCameraBy(np.array([0.0, 0.0, 1.0], dtype=np.float32))
                    if (event.key == pg.K_SPACE):
                        self.camera.moveCameraBy(np.array([0.0, 1.0, 0.0], dtype=np.float32))
                    if (event.key == pg.K_LCTRL):
                        self.camera.moveCameraBy(np.array([0.0, -1.0, 0.0], dtype=np.float32))
                    if (event.key == pg.K_RIGHT):
                        self.camera.spinCamera(10, 0)
                    if (event.key == pg.K_LEFT):
                        self.camera.spinCamera(-10, 0)
                    if (event.key == pg.K_UP):
                        self.camera.spinCamera(0, 10)
                    if (event.key == pg.K_DOWN):
                        self.camera.spinCamera(0, -10)

            # Refresh the screen
            glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

            # Draw all objects
            self.drawObjects()

            # Reinitialize matrices after all computation has been done
            self.GLUtils.initMatrices()

            # Animate camera
            self.animateCamera()

            # Refresh screen
            pg.display.flip()

            # Increment the clock
            self.clock.tick(60)
        self.quit()
    
    def destroyObjects(self):
        for obj in self.objects:
            obj.destroy()

    def quit(self):
        self.destroyObjects()
        self.GLUtils.quit(self.objects)

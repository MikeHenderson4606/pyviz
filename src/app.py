import pygame as pg
from OpenGL.GL import *
import numpy as np
import ctypes
from OpenGL.GL.shaders import compileProgram, compileShader
from OpenGL.GLU import *
from abc import ABC, abstractmethod
import pyrr

from src.GLUtils import GLUtils
from src.Animations import Animations
from src.Line import Line
from src.Circle import Circle
from src.Simulation import Simulation
from src.Triangle import Triangle
from src.Arrow import Arrow
from src.Quad import Quad
from src.Camera import Camera
from src.VObject import VObject
from src.utils import MathUtils
from src.objtypes import Colors

class App:

    def __init__(self, width, height):
        # Instantiate Application
        self.objects = []
        self.sims = []
        self.quads = []
        self.steps = 350
        self.clock = pg.time.Clock()
        self.running = True

        # Generate initial view matrix camera coords
        self.camera = Camera()

        # Create animation class
        self.animator = Animations()

        # Create OpenGL utils class
        self.GLUtils = GLUtils(width, height, self.camera)

        # Create utils class
        self.utils = MathUtils()

    def createAxes3D(self, hash_length=0.12, hash_thickness=1, x_min = -10, x_max = 10, y_min = -10, y_max = 10, z_min=-10, z_max=10):
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

    def createAxes2D(self, hash_length=0.12, hash_thickness=1, x_min=-10, x_max=10, y_min=-10, y_max=10):
        x_axis = Line([x_min, 0.0, 0.0], [x_max, 0.0, 0.0], thickness=3)
        y_axis = Line([0.0, y_min, 0.0], [0.0, y_max, 0.0], thickness=3)
        for i in range(int(x_max - x_min)):
            x_interval = i
            x_hash = Line([x_min + x_interval, hash_length / 2, 0.0], [x_min + x_interval, -hash_length / 2, 0.0], thickness=hash_thickness)
            self.addObject(x_hash)
            
        for i in range(int(y_max - y_min)):
            y_interval = i
            y_hash = Line([hash_length / 2, y_min + y_interval, 0.0], [-hash_length / 2, y_min + y_interval, 0.0], thickness=hash_thickness)
            self.addObject(y_hash)

        self.addObject(x_axis)
        self.addObject(y_axis)

    def addObject(self, obj):
        if (isinstance(obj, VObject)):
            if (isinstance(obj, Quad)):
                self.quads.append(obj)
            else:
                self.objects.append(obj)
            # Creating vertices
            obj.createVertices()
            # Instantiating objects
            obj.instantiateGLObjects()
            # Check for errors
            # self._checkGLErrors()
            # Sort the object back into the list of objects
            self.calculatePriorities()
        else:
            raise Exception("Must input a valid VObject for the application.")

    def addSimulation(self, sim):
        if (isinstance(sim, Simulation)):
            sim.addApp(self)
            sim.Render()
            self.sims.append(sim)
        else:
            raise Exception("Please input a valid Simulation.")

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

    def draw3DFunction(self, func, lower, upper, steps=25, normals=False):
        di = (upper - lower) / (steps - 1)
        x_values = np.linspace(lower, upper, steps)
        y_values = np.linspace(lower, upper, steps)
        for index_x, x_val in enumerate(x_values):
            for index_y, y_val in enumerate(y_values):
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
                quad = Quad(vertices=vertices, color=Colors.MAGENTA.value)
                self.addObject(quad)

                # Normals
                if (normals and (index_x + index_y) % 4 == 0):
                    normal = np.cross(vertices[1] - vertices[0], vertices[2] - vertices[0])
                    unit_normal = normal / np.linalg.norm(normal)
                    normal = Arrow(start=vertices[0], end=(vertices[0] - (unit_normal * 0.5)), color=Colors.YELLOW.value)
                    self.addObject(normal)

    def runSimulations(self):
        for sim in self.sims:
            sim.Update()

    def drawObjects(self):
        # Initialize all other objects which exist without the special shader
        for obj in self.objects:
            # Set shader
            self.setShader(obj)
            obj.updatePosition()
            if (isinstance(obj, Arrow)):
                length = obj.end - obj.start
                if (np.linalg.norm(length) > 0.1):
                    obj.draw()
            else:
                obj.draw()
        # Initialize matrices
        self.GLUtils.initMatrices()
        # Initialize all the quads at once, which are transparent and shaded
        for quad in self.quads:
            self.setShader(quad)
            quad.draw()
        self.GLUtils.initMatrices()

    def setShader(self, obj):
        if (isinstance(obj, Quad)):
            self.GLUtils.setTranslucentShader()
        else:
            self.GLUtils.setDefaultShader()

    def moveCamera(self, pos, focus, animate=False):
        pos = np.array(pos, dtype=np.float32)
        focus = np.array(focus, dtype=np.float32)
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

    def handleInput(self, events):
        for event in events:
            if (event.type == pg.QUIT):
                self.running = False
            if (event.type == pg.KEYDOWN):
                if (event.key == pg.K_ESCAPE):
                    self.running = False
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

    def run(self):
        while (self.running):
            glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

            # Handle input
            self.handleInput(pg.event.get())

            # Run any similations
            self.runSimulations()

            # Draw all objects
            self.drawObjects()

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

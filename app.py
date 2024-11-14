import pygame as pg
from OpenGL.GL import *
import numpy as np
import ctypes
from OpenGL.GL.shaders import compileProgram, compileShader
from OpenGL.GLU import *
from abc import ABC, abstractmethod
import pyrr

from Line import Line
from Circle import Circle
from Triangle import Triangle
from Camera import Camera

class App:

    def __init__(self, width, height):
        # Initializing pygame
        self.width = width
        self.height = height
        # Calculate aspect ratio
        self.aspect_ratio = self.width / self.height
        self.objects = []
        self.steps = 350
        self.initPyGame(width, height)
        # Generate initial view matrix camera coords
        self.camera = Camera()
        
        # Initializing OpenGL
        self.initOpenGL()

        # Initialize MVP matrices
        self.initMatrices()

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

    def initPyGame(self, width, height):
        pg.init()

        # Request OpenGL 3.3 core profile context
        pg.display.gl_set_attribute(pg.GL_CONTEXT_MAJOR_VERSION, 4)
        pg.display.gl_set_attribute(pg.GL_CONTEXT_MINOR_VERSION, 1)
        pg.display.gl_set_attribute(pg.GL_CONTEXT_PROFILE_MASK, pg.GL_CONTEXT_PROFILE_CORE)

        # Enable anti-aliasing
        pg.display.gl_set_attribute(pg.GL_MULTISAMPLEBUFFERS, 1)
        pg.display.gl_set_attribute(pg.GL_MULTISAMPLESAMPLES, 4)  # 4x anti-aliasing
        
        pg.display.set_mode((width, height), pg.OPENGL|pg.DOUBLEBUF)

        glEnable(GL_MULTISAMPLE)
        glEnable(GL_DEPTH_TEST)
        glEnable(GL_CULL_FACE)
        self.clock = pg.time.Clock()

    def initOpenGL(self):
        glClearColor(0.3, 0.3, 0.3, 1)
        glViewport(0, 0, self.width, self.height)
        self._checkGLErrors()

    def initPerspective(self):
        # Set up perspective projection
        self.projection_matrix = self.generatePerspectiveMatrix(45, 0.1, 20.0)

        projection_location = glGetUniformLocation(self.shader, 'projection')
        if (projection_location >= 0):
            glUniformMatrix4fv(projection_location, 1, GL_FALSE, self.projection_matrix)
        else:
            print("Something went wrong assigning uniform variable: projection.")

    def generatePerspectiveMatrix(self, fov, near, far):
        perspective_matrix = pyrr.matrix44.create_perspective_projection_matrix(
            fov, 
            self.aspect_ratio, 
            near, 
            far, 
            dtype=np.float32
        )

        return perspective_matrix

    def initView(self):
        # Generate view matrix
        self.view_matrix = self.camera.getViewMatrix()

        # Generate bounds
        self.lower_bound, self.upper_bound = self.calculateBounds(self.camera.camera_eye)

        view_location = glGetUniformLocation(self.shader, 'view')
        if (view_location >= 0):
            glUniformMatrix4fv(view_location, 1, GL_FALSE, self.view_matrix)
        else:
            print("Something went wrong assigning uniform variable: view.")

    def initModel(self):
        self.model = np.identity(4, dtype=np.float32)

        model_location = glGetUniformLocation(self.shader, 'model')
        if (model_location >= 0):
            glUniformMatrix4fv(model_location, 1, GL_FALSE, self.model)
        else:
            print("Something went wrong assigning uniform variable: model.")

    def _checkGLErrors(self):
        # Add this line to print OpenGL version
        print(f"OpenGL Version: {glGetString(GL_VERSION).decode()}")
        error = glGetError()
        if error != GL_NO_ERROR:
            print(f"OpenGL error: {error}")
        else:
            print("There are no OpenGL errors")

    def initShaders(self, vertFilePath, fragFilePath):
        self.shader = self.createShader(vertFilePath, fragFilePath)
        glUseProgram(self.shader)

    def createShader(self, vertFilePath, fragFilePath):
        with open(vertFilePath, 'r') as f:
            vert_src = f.read()

        with open(fragFilePath, 'r') as f:
            frag_src = f.read()

        try:
            shader = compileProgram(
                compileShader(vert_src, GL_VERTEX_SHADER),
                compileShader(frag_src, GL_FRAGMENT_SHADER)
            )
            return shader
        except RuntimeError as e:
            print(f'Shader compilation error: {e}')
            return None

    def addObject(self, obj):
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

    def initMatrices(self):
        # Bind to a default VAO
        self.default_vao = glGenVertexArrays(1)
        glBindVertexArray(self.default_vao)
        # Initialize Shaders
        self.initShaders("./shaders/vert.txt", "./shaders/frag.txt")
        # Set up matrices
        self.initPerspective()
        self.initView()
        self.initModel()
        # Unbind the VAO
        glBindVertexArray(0)

    def calculateBounds(self, eye):
        fov = 45
        #       tan of fov / 2    eye z position
        x = np.tan(fov / 2) * eye[2] * self.aspect_ratio
        lower_bound = eye[0] - x
        upper_bound = eye[0] + x
        return lower_bound, upper_bound

    def createFunctionAnimation(self, obj, func, loop, draw=True):
        discontinuity_threshold = 100
        obj.steps = self.steps
        obj.potential_discontinuities = []
        obj.doesLoop = loop
        obj.doesAnimate = True
        obj.drawFunc = draw

        interval = (self.upper_bound - self.lower_bound) / obj.steps
        loopIndices = np.arange(self.lower_bound, self.upper_bound, interval)
        for i in loopIndices:
            try:
                obj.animation_steps.append([float(i), float(func(i)), 0.0])
                if abs(func(i) - func(i - interval)) > discontinuity_threshold:
                    obj.potential_discontinuities.append(i)
            except:
                print("Out of range.")
                pass

    def animate(self, obj):
        if (obj.doesLoop):
            if (obj.currStep >= (obj.steps - 1)):
                self.removeObjects(obj.lines)
                obj.lines = []
                obj.currStep = 0
            elif (len(obj.animation_steps) > 0):
                obj.updatePosition(obj.animation_steps[obj.currStep])
                self.animateFuncDrawing(obj, obj.animation_steps[obj.currStep], obj.animation_steps[obj.currStep + 1])
                obj.currStep += 1
        else:
            if (obj.currStep >= (obj.steps - 1)):
                obj.doneCycle = True
            elif (len(obj.animation_steps) > 0 and not obj.doneCycle):
                obj.updatePosition(obj.animation_steps[obj.currStep])
                if (obj.drawFunc):
                    self.animateFuncDrawing(obj, obj.animation_steps[obj.currStep], obj.animation_steps[obj.currStep + 1])
                obj.currStep += 1

    def drawFunction(self, func):
        steps = self.steps
        di = (self.upper_bound - self.lower_bound) / steps
        x_values = np.arange(self.lower_bound, self.upper_bound, step=di)
        for i in x_values:
            try:
                line = Line([i, func(i), 0.0], [i + di, func(i + di), 0.0], color=(0, 0, 0), thickness=2, z_index = 1)
                self.addObject(line)
            except:
                # Ignore drawing any out of range x values
                print("Out of range.")
                pass

    def animateFuncDrawing(self, obj, val, nextVal):
        if all(not (val[0] <= discont <= nextVal[0]) for discont in obj.potential_discontinuities):
            line = Line([val[0], val[1], val[2]], [nextVal[0], nextVal[1], nextVal[2]], color=(0, 0, 0), thickness=2, z_index = 1)
            obj.lines.append(line)
            self.addObject(line)
        else:
            print("hit potential discontinuity at: " + str(val[0]))

    def drawObjects(self):
        for obj in self.objects:
            if (obj.doesAnimate):
                self.animate(obj)
            obj.draw()

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
                        self.camera.moveCameraBy(np.array([0.0, 1.0, 0.0], dtype=np.float32))  
                    if (event.key == pg.K_s):
                        self.camera.moveCameraBy(np.array([0.0, -1.0, 0.0], dtype=np.float32))
                    if (event.key == pg.K_RIGHT):
                        self.camera.spinCamera(10, 0)
                    if (event.key == pg.K_LEFT):
                        self.camera.spinCamera(-10, 0)
                    if (event.key == pg.K_UP):
                        self.camera.spinCamera(0, 10)
                    if (event.key == pg.K_DOWN):
                        self.camera.spinCamera(0, -10)
                # Reinitialize matrices once a key press has happened
                self.initMatrices()

            # Refresh the screen
            glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

            # Draw all objects
            self.drawObjects()

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
        if (len(self.objects) > 0):
            glDeleteProgram(self.shader)
        pg.quit()

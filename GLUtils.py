
import pygame as pg
from OpenGL.GL import *
import numpy as np
import ctypes
from OpenGL.GL.shaders import compileProgram, compileShader
from OpenGL.GLU import *
from abc import ABC, abstractmethod
import pyrr

class GLUtils:

    def __init__(self, width, height, camera):
        if (width > 0):
            self.width = width
        else:
            raise Exception("Please input a valid width.")
        
        if (height > 0):
            self.height = height
        else:
            raise Exception("Please input a valid height.")
        
        if (camera):
            self.camera = camera
        else:
            raise Exception("Please include a camera.")
        
        self.aspect_ratio = self.width / self.height

        # Initialize PyGame
        self.initPyGame(width, height)

        # Initializing OpenGL
        self.initOpenGL()

        # Initialize MVP matrices
        self.initMatrices()

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

    def initOpenGL(self):
        glClearColor(0.3, 0.3, 0.3, 1)
        glViewport(0, 0, self.width, self.height)
        self.__checkGLErrors()

    def __checkGLErrors(self):
        # Add this line to print OpenGL version
        print(f"OpenGL Version: {glGetString(GL_VERSION).decode()}")
        error = glGetError()
        if error != GL_NO_ERROR:
            print(f"OpenGL error: {error}")
        else:
            print("There are no OpenGL errors")

    def calculateBounds(self, eye):
        fov = 45
        #       tan of fov / 2    eye z position
        x = np.tan(fov / 2) * eye[2] * self.aspect_ratio
        lower_bound = eye[0] - x
        upper_bound = eye[0] + x
        return lower_bound, upper_bound

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

    def initPerspective(self):
        # Set up perspective projection
        self.projection_matrix = self.__generatePerspectiveMatrix(45, 0.1, 50.0)

        projection_location = glGetUniformLocation(self.shader, 'projection')
        if (projection_location >= 0):
            glUniformMatrix4fv(projection_location, 1, GL_FALSE, self.projection_matrix)
        else:
            print("Something went wrong assigning uniform variable: projection.")

    def __generatePerspectiveMatrix(self, fov, near, far):
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
    
    def quit(self, objects):
        if (len(objects) > 0):
            glDeleteProgram(self.shader)
        pg.quit()
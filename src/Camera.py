from tracemalloc import start
import numpy as np
from pygame import init
import pyrr
from src.utils import MathUtils

class Camera():

    def __init__(self):
        self.camera_eye = np.array([0.0, 0.0, 10.0], dtype=np.float32)  # Camera is some units back along the z-axis
        self.camera_forwards = np.array([0.0, 0.0, -1.0], dtype=np.float32) # Looking down the z axis
        self.up = np.array([0.0, 1.0, 0.0], dtype=np.float32)  # 'Up' is along the positive y-axis
        self._camera_speed = 0.05
        self.camera_focus = np.array([0, 0, 0], dtype=np.float32)
        self.camera_animation = []
        self.curr_step = 0
        self.max_steps = 0
        self.theta = 0
        self.phi = 0
        self.utils = MathUtils()

        self.updateVectors()

    def updateVectors(self):
        self.forwards = np.array([
            np.sin(np.deg2rad(self.theta)),
            np.sin(np.deg2rad(self.phi)),
            -np.cos(np.deg2rad(self.theta))
        ], dtype=np.float32)

        globalUp = np.array([0.0, 1.0, 0.0], dtype=np.float32)
        
        # Fundamental 3 directions
        self.right = np.cross(self.forwards, globalUp)          # Right vector
        self.up = np.cross(self.right, self.forwards)           # Up vector

    def _lookAt(self):
        # Ensure camera is looking down z axis
        view_matrix = pyrr.matrix44.create_look_at(
            eye = self.camera_eye,
            target = self.camera_eye + self.forwards,
            up = self.up,
            dtype=np.float32
        )

        return view_matrix

    def moveCameraBy(self, newPos):
        newPos = np.array(newPos, dtype=np.float32)
        self.camera_eye += newPos

    def spinCamera(self, dTheta, dPhi):
        self.theta += dTheta
        if self.theta > 360:
            self.theta -= 360
        elif self.theta < 0:
            self.theta += 360

        self.phi += dPhi

        self.updateVectors()

    def moveCamera(self, pos, focus):
        self.camera_eye = pos

        deltax = focus[0] - pos[0]
        deltay = focus[1] - pos[1]
        deltaz = -(focus[2] - pos[2])

        self.theta = np.rad2deg(np.arctan2(deltax, deltaz))
        h = np.sqrt(deltax**2 + deltaz**2)
        self.phi = np.rad2deg(np.arctan2(deltay, h))

        # self.camera_animation = [self.camera_eye]
        self.camera_focus = focus

        self.updateVectors()

    def incrementStep(self):
        self.curr_step += 1

    def generateCameraPositions(self, endPos, focus, steps=25):
        lower_gaussian = -0.9575
        upper_gaussian = 0.9575
        # Range over the gaussian from -3 to 3 in steps of 1 / steps
        a = np.arange(lower_gaussian, upper_gaussian, (upper_gaussian - (lower_gaussian)) / steps)
        # The next value is going to be 1 / steps past the a value
        b = a + (1 / steps)
        # Find out the length of the vector
        startPos = self.camera_animation[self.max_steps] if (len(self.camera_animation) > 0) else self.camera_eye
        diff = endPos - startPos
        xpositions = []
        ypositions = []
        zpositions = []
        self.camera_focus = focus
        for i in range (len(a)):
            # The area of the gaussian between a and b, multiplied by 100 to determine how many points fall within that interval
            area = self.utils.computeGaussianIntegral(a[i], b[i])
            # Calculate starting positions of the ranges
            startX = startPos[0] + (diff[0] * i / steps)
            endX = startPos[0] + (diff[0] * (i + 1) / steps)
            startY = startPos[1] + (diff[1] * i / steps)
            endY = startPos[1] + (diff[1] * (i + 1) / steps)
            startZ = startPos[2] + (diff[2] * i / steps)
            endZ = startPos[2] + (diff[2] * (i + 1) / steps)

            xpos = [startX] * area if (diff[0] == 0 or area == 0) else (np.linspace(startX, endX, area, dtype=np.float32))
            ypos = [startY] * area if (diff[1] == 0 or area == 0) else (np.linspace(startY, endY, area, dtype=np.float32))
            zpos = [startZ] * area if (diff[2] == 0 or area == 0) else (np.linspace(startZ, endZ, area, dtype=np.float32))

            xpositions.extend(xpos)
            ypositions.extend(ypos)
            zpositions.extend(zpos)
        
        for i in range(len(xpositions)):
            self.camera_animation.append(np.array([
                xpositions[i], ypositions[i], zpositions[i]
            ], dtype=np.float32))
        self.max_steps += len(xpositions) - 1

    def getViewMatrix(self):
        return self._lookAt()

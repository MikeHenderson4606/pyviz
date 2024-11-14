import numpy as np
import pyrr

class Camera():

    def __init__(self):
        self.camera_eye = np.array([0.0, 0.0, 10.0])  # Camera is some units back along the z-axis
        self.camera_forwards = np.array([0.0, 0.0, -1.0]) # Looking down the z axis
        self.up = np.array([0.0, 1.0, 0.0])  # 'Up' is along the positive y-axis
        self._camera_speed = 0.05
        self.theta = 0
        self.phi = 0

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
        print(self.forwards)

    def getViewMatrix(self):
        return self._lookAt()

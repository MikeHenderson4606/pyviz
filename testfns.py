from random import sample
from src.Simulation import Simulation
from src.app import App
from src.Circle import Circle
from src.Triangle import Triangle
from src.Line import Line
from src.Arrow import Arrow
from src.objtypes import *
from src.objtypes import PositionTypes as pt
from src.utils import MathUtils as mt
from typing import List
import numpy as np

def trigFunc(x):
    return np.cos(x) * np.sin(x) / np.arctan(x)

def logFunc(x):
    if (x > 0):
        return np.log2(x)
    else:
        return -100

def negLog(x):
    if (x > 0):
        return logFunc(-x)
    else:
        return -100

def basicFunc(x):
    return np.sqrt(x)

def findDistance(x, y):
    return np.sqrt(np.pow(x, 2) + np.pow(y, 2))

def test3D(x, y):
    # r = findDistance(x, y)
    # return np.sin(x) / r
    return test3D2(x, y) - 3

def test3D2(x, y):
    return np.cos(x) * np.sin(y) + 3

class TestSimulation(Simulation):
    def __init__(self):
        super().__init__()
        self.arrows = []

    def Render(self):
        # Create grid of arrows
        lower = -10
        upper = 10
        steps = 25
        x_values = np.linspace(lower, upper, steps)
        y_values = np.linspace(lower, upper, steps)
        for x_val in x_values:
            for y_val in y_values:
                length = np.array([0.0, 0.5, 0.0], dtype=np.float32)
                start = np.array([x_val, 0, y_val], dtype=np.float32)
                arrow = Arrow(start, start + length)
                self.app.addObject(arrow)
                self.arrows.append(arrow)
    
    def Update(self):
        for arrow in self.arrows:
            position = arrow.start
            dist = np.sqrt(np.pow(position[0], 2) + np.pow(position[1], 2) + np.pow(position[2], 2))
            if (dist != 0):
                newPosition = ArrowPosition(arrow.start, pt.createArray(arrow.end[0], (np.sin(self.iteration / 10) + 1) / (dist * dist), arrow.end[2]))
            else:
                newPosition = ArrowPosition(arrow.start, pt.createArray(arrow.end[0], 0, arrow.end[2]))
            arrow.updatePosition(newPosition)
        self.iteration += 1

class Particle:
        def __init__(self, position, velocity, mass):
            self.position = position
            self.velocity = velocity
            self.mass = mass

class FluidSimulation(Simulation):
    def __init__(self):
        super().__init__()
        self.points: List[Circle] = []
        self.particles: List[Particle] = []
        # Predicted positions
        self.predicted_positions = []
        # Densities for each particle
        self.densities = []
        # Width of the border
        self.width = 2.5
        # Height of the border
        self.height = 3
        # Gravity -> scaled for visuals
        self.gravity = 10
        # Dampen the collisions
        self.dampeningConstant = 0.8
        # The time control
        self.deltaTime = 1 / 120
        # Smoothing distance
        self.smoothingDistance = 2.0
        # Target density
        self.targetDensity = 0.5

    def drawBorder(self):
        particle_radius = 0.08
        bottom_left = pt.createArray(-self.width - particle_radius, -self.height - particle_radius, 0)
        bottom_right = pt.createArray(self.width + particle_radius, -self.height - particle_radius, 0)
        top_right = pt.createArray(self.width + particle_radius, self.height + particle_radius, 0)
        top_left = pt.createArray(-self.width - particle_radius, self.height + particle_radius, 0)

        border_top = Line(top_left, top_right)
        border_right = Line(top_right, bottom_right)
        border_bottom = Line(bottom_right, bottom_left)
        border_left = Line(bottom_left, top_left)

        self.app.addObject(border_top)
        self.app.addObject(border_right)
        self.app.addObject(border_bottom)
        self.app.addObject(border_left)

    def Render(self):
        # Create grid of particles
        lower = - self.width / 2
        upper = self.height / 2
        steps = 5
        x_values = np.linspace(lower, upper, steps)
        y_values = np.linspace(lower, upper, steps)
        self.densities = [0] * (steps * steps)
        for x_index, x_val in enumerate(x_values):
            for y_index, y_val in enumerate(y_values):
                position = pt.createArray(x_val, y_val, 0)
                velocity = pt.createArray(0, 0, 0)

                point = Circle(radius=0.4, center=position)
                self.points.append(point)
                self.app.addObject(point)

                particle = Particle(position=position, velocity=velocity, mass=1.0)
                self.predicted_positions.append(position)
                self.particles.append(particle)

        self.drawBorder()
    
    def Update(self):
        for index, particle in enumerate(self.particles):
            self.applyGravitationalForces(index)

            self.applyPressureForces(index)

            self.handleCollisions(particle)

            self.updatePositions(index)
    
    def applyGravitationalForces(self, index):
        self.particles[index].velocity += mt.Down() * self.gravity * self.deltaTime
        self.predicted_positions[index] = self.particles[index].position + (self.particles[index].velocity * self.deltaTime)

        self.densities[index] = self.calculateDensity(index)
    
    def applyPressureForces(self, index):
        pressure_force = self.calculatePressureForce(index)
        pressure_acceleration = pt.createArray(0, 0, 0)
        
        if (self.densities[index] != 0):
            pressure_acceleration = pressure_force / self.densities[index]

        self.particles[index].velocity += pressure_acceleration * self.deltaTime 

    def updatePositions(self, index):
        self.particles[index].position += self.particles[index].velocity * self.deltaTime
        newPosition = CirclePosition(center=self.particles[index].position)

        self.points[index].updatePosition(newPosition)

    def handleCollisions(self, part):
        if (isinstance(part, Particle)):
            if (np.abs(part.position[0]) >= self.width):
                part.position[0] = np.sign(part.position[0]) * self.width
                part.velocity[0] *= -self.dampeningConstant
            if (np.abs(part.position[1]) >= self.height):
                part.position[1] = np.sign(part.position[1]) * self.height
                part.velocity[1] *= -self.dampeningConstant

    def calculatePressureForce(self, sampleIndex):
        pressure_force = pt.createArray(0, 0, 0)

        for index, particle in enumerate(self.particles):
            if (index == sampleIndex): continue

            offset = self.predicted_positions[index] - self.predicted_positions[sampleIndex]
            dist = np.linalg.norm(offset)
            dir = offset / dist if dist != 0 else np.array([0, 0, 0], dtype=np.float32)

            slope = self.smoothingKernelDerivative(dist)
            density = self.densities[index]
            sharedPressure = self.calculateSharedPressure(density, self.densities[sampleIndex])

            if (density != 0):
                pressure_force += sharedPressure * dir * self.particles[sampleIndex].mass * slope / density

        return pressure_force
    
    def calculateDensity(self, sampleIndex):
        density = 0

        for index, particle in enumerate(self.particles):
            dist = np.linalg.norm(self.predicted_positions[sampleIndex] - self.predicted_positions[index])
            influence = self.smoothingKernel(dist)

            density += self.particles[sampleIndex].mass * influence
        
        return density

    def calculateSharedPressure(self, density1, density2):
        pressure1 = density1 - self.targetDensity
        pressure2 = density2 - self.targetDensity
        return (pressure1 + pressure2) / 2

    def smoothingKernel(self, dist):
        if (dist >= self.smoothingDistance): return 0

        volume = np.pi * np.pow(self.smoothingDistance, 4) / 2
        return np.pow(self.smoothingDistance - dist, 3) / volume
    
    def smoothingKernelDerivative(self, dist):
        if (dist >= self.smoothingDistance): return 0

        return -3 * np.pow(self.smoothingDistance - dist, 2)


if __name__ == "__main__":
    width = 1200
    height = 720

    app = App(width, height)
    sim = FluidSimulation()

    app.moveCamera([0, 0, 10], [0, 0, 0])
    app.addSimulation(sim)
    app.run()

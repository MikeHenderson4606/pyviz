from typing import List
import numpy as np
from src.Circle import Circle
from src.Line import Line
from src.Quad import Quad
from src.Simulation import Simulation
from src.Tile import Tile
from src.objtypes import CirclePosition, PositionTypes as pt
from src.utils import MathUtils as mt
from src.utils import HashTable as ht

class Particle:
    def __init__(self, position, velocity, mass):
        self.position = position
        self.velocity = velocity
        self.mass = mass

class Cell:
    def __init__(self, particles: List[Particle], x, y, _id):
        self.particles = particles
        self.x = x
        self.y = y
        self._id = _id

class FluidSimulation(Simulation):
    def __init__(self, width, height, smoothing_dist, mu=0.1, show_particles=True, show_background=False):
        super().__init__()
        self.points: List[Circle] = []
        self.particles: List[Particle] = []
        # Hash table to store values
        self.cells: List[Tile] = [] # Visual cells
        self.grid: List[Cell] = []  # Hashed cells
        # Predicted positions
        self.predicted_positions = []
        # Densities for each particle
        self.densities = []
        # Width of the border
        self.width = width
        # Height of the border
        self.height = height
        # Gravity
        self.gravity = 10
        # Dampen the collisions
        self.dampeningConstant = 0.6
        # The time control
        self.deltaTime = 1 / 120
        # Viscosity factor
        self.mu = mu
        # Smoothing distance
        self.smoothingDistance = smoothing_dist
        # Target density
        self.targetDensity = 30
        # Show the particles or not 
        self.show_particles = show_particles
        # Show the background or not
        self.show_background = show_background

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
        self.createHashTable()

        # The box of particles to start with
        lower = -self.width / 4
        upper = self.height / 4
        steps = 10
        x_values = np.linspace(lower, upper, steps)
        y_values = np.linspace(lower, upper, steps)
        self.densities = [0] * (steps * steps)
        for x_index, x_val in enumerate(x_values):
            for y_index, y_val in enumerate(y_values):
                position = pt.createArray(x_val, y_val, 0)
                velocity = pt.createArray(0, 0, 0)

                if (self.show_particles):
                    point = Circle(radius=0.4, center=position, z_index=50)
                    self.points.append(point)
                    self.app.addObject(point)

                particle = Particle(position=position, velocity=velocity, mass=1.0)
                index = self.calculatePosition(particle)
                self.grid[index].particles.append(particle)

                self.predicted_positions.append(position)
                self.particles.append(particle)

        # raise Exception("Halt")
        self.drawBorder()

    def Update(self):
        for index, particle in enumerate(self.particles):
            # Handle collisions with walls
            self.handleCollisions(particle)
            # Apply gravitational forces
            self.applyGravitationalForces(index)
            # Apply pressure forces
            self.applyPressureForces(index)
            # Update positions of particles
            self.updatePositions(index)
    
    def createHashTable(self):
        # Create a grid (hash table) to check neighoring cells more efficiently
        buffer = 0.0001
        if ((self.width % self.smoothingDistance >= buffer and 
             (self.width % self.smoothingDistance) <= (self.smoothingDistance - buffer)) or
            (self.height % self.smoothingDistance >= buffer and
             self.height % self.smoothingDistance <= (self.smoothingDistance - buffer))):
            # Checks for when the modulo is somewhere close to 0 or the smoothing distance
            raise Exception("Please ensure the smoothing distance is a multiple of the width and height")
        
        # print(self.width * 2 / self.smoothingDistance)
        # print(self.width * 2 / (self.width * 2 / self.smoothingDistance))
        cols = np.linspace(-self.width, self.width, round(self.width * 2 / self.smoothingDistance), endpoint=False)
        rows = np.linspace(self.height, -self.height, round(self.height * 2 / self.smoothingDistance), endpoint=False)
        result = (2 * self.width / self.smoothingDistance) * (2 * self.height / self.smoothingDistance)
        grid_range = round(result)
        self.grid: List[Cell] = []
        print(grid_range)
        for i in range(grid_range):
            x_val = self.smoothingDistance * (i % len(cols))
            y_val = (2 * self.height) - (self.smoothingDistance * int(i / len(rows)))
            curr_cell = Cell(particles=[], 
                                  x=x_val, 
                                  y=y_val,
                                  _id=i)
            self.grid.append(curr_cell)
            
        if (self.show_background):
            for row_index, row in enumerate(rows):
                for col_index, col in enumerate(cols):
                    cell = Tile(np.array([pt.createArray(col, row, 0),
                                        pt.createArray(col + self.smoothingDistance, row, 0),
                                        pt.createArray(col, row - self.smoothingDistance, 0),
                                        pt.createArray(col + self.smoothingDistance, row - self.smoothingDistance, 0)], dtype=np.float32),
                                color=mt.createColor(0, 0, 0),
                                z_index=0)
                    self.app.addObject(cell)
                    self.cells.append(cell)

    def calculatePosition(self, particle):
        if (isinstance(particle, Particle)):
            rows = round(2 * self.height / self.smoothingDistance)
            position = particle.position + np.array([self.width, self.height, 0], dtype=np.float32)

            col = round(position[0] / self.smoothingDistance)
            row = rows - round(position[1] / self.smoothingDistance) - 1

            if (col == round(2 * self.width / self.smoothingDistance)):
                col = round(2 * self.width / self.smoothingDistance) - 1

            return col + (rows * row)

    def applyGravitationalForces(self, index):
        self.particles[index].velocity += mt.Down() * self.gravity * self.deltaTime
        self.predicted_positions[index] = self.particles[index].position + (self.particles[index].velocity * self.deltaTime)

        self.densities[index] = self.calculateDensity(index)
    
    def applyPressureForces(self, index):
        net_force = self.calculateForces(index)
        pressure_acceleration = pt.createArray(0, 0, 0)
        
        if (self.densities[index] != 0):
            pressure_acceleration = net_force / self.densities[index]

        self.particles[index].velocity += pressure_acceleration

    def updatePositions(self, index):
        oldCell = self.calculatePosition(self.particles[index])

        self.particles[index].position += self.particles[index].velocity * self.deltaTime

        newCell = self.calculatePosition(self.particles[index])
        # Swap the positions in the table
        if (oldCell != newCell):
            self.grid[oldCell].particles.remove(self.particles[index])
            self.grid[newCell].particles.append(self.particles[index])
            
            if (self.show_background):
                particle_count_new = len(self.grid[newCell].particles)
                particle_count_old = len(self.grid[oldCell].particles)
                newColor = mt.createColor(0, 0, np.min([particle_count_new * 35, 255]))
                oldColor = mt.createColor(0, 0, np.min([particle_count_old * 35, 255]))
                self.cells[newCell].updateColor(newColor)
                self.cells[oldCell].updateColor(oldColor)

        if (self.show_particles):
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

    def createCellsToCheck(self, curr_cell_index):
        this_cell = self.grid[curr_cell_index]
        rows = round((2 * self.height) / self.smoothingDistance)
        cols = round((2 * self.width) / self.smoothingDistance)

        # Get all relevant cells - check width
        if (curr_cell_index % cols == 0):
            # Left wall
            top_left_cell = left_cell = bottom_left_cell = None
        elif (curr_cell_index % cols == cols - 1):
            # Right wall
            top_right_cell = right_cell = bottom_right_cell = None

        if (int(curr_cell_index / rows) == 0):
            # Top wall
            top_left_cell = top_middle_cell = top_right_cell = None
        elif (int(curr_cell_index / rows) == rows - 1):
            # Bottom wall
            bottom_left_cell = bottom_middle_cell = bottom_right_cell = None

        top_left_cell = self.grid[round(curr_cell_index - cols - 1)] if not ('top_left_cell' in locals()) else None
        top_middle_cell = self.grid[round(curr_cell_index - cols)] if not ('top_middle_cell' in locals()) else None
        top_right_cell = self.grid[round(curr_cell_index - cols + 1)] if not ('top_right_cell' in locals()) else None
        left_cell = self.grid[round(curr_cell_index - 1)] if not ('left_cell' in locals()) else None
        right_cell = self.grid[round(curr_cell_index + 1)] if not ('right_cell' in locals()) else None
        bottom_left_cell = self.grid[round(curr_cell_index + cols - 1)] if not ('bottom_left_cell' in locals()) else None
        bottom_middle_cell = self.grid[round(curr_cell_index + cols)] if not ('bottom_middle_cell' in locals()) else None
        bottom_right_cell = self.grid[round(curr_cell_index + cols + 1)] if not ('bottom_right_cell' in locals()) else None

        # Put them all in an array
        cells_to_check = [top_left_cell, 
                          top_middle_cell, 
                          top_right_cell, 
                          left_cell, 
                          this_cell, 
                          right_cell, 
                          bottom_left_cell, 
                          bottom_middle_cell, 
                          bottom_right_cell]
        
        return cells_to_check

    def calculateForces(self, sampleIndex):
        net_force = pt.createArray(0, 0, 0)
        # Pressure forces
        pressure_force = pt.createArray(0, 0, 0)
        # Viscosity forces
        viscosity_force = pt.createArray(0, 0, 0)

        # Try to do the new grid system instead of the O(n^2)
        curr_particle = self.particles[sampleIndex]
        curr_cell_index = int(self.calculatePosition(curr_particle))

        # Initialize all as none first
        cells_to_check = self.createCellsToCheck(curr_cell_index)
        
        # Ideally faster O(mn)
        for cell in cells_to_check:
            if (cell):
                for particle in cell.particles:
                    if (particle == self.particles[sampleIndex]): continue

                    # Used for both force calculations
                    particle_index = self.particles.index(particle)
                    offset = self.predicted_positions[particle_index] - self.predicted_positions[sampleIndex]
                    dist = np.linalg.norm(offset)
                    density = self.densities[particle_index]
                    dir = offset / dist if dist != 0 else np.array([0, 0, 0], dtype=np.float32)

                    # Viscosity forces
                    mass = particle.mass
                    velocity_1 = self.particles[sampleIndex].velocity
                    velocity_2 = particle.velocity
                    v_slope = self.smoothingKernelViscosity(dist)
                    
                    if (density != 0):
                        viscosity_force += mass * (velocity_2 - velocity_1) * v_slope / density 

                    # Pressure forces
                    slope = self.smoothingKernelDerivative(dist)
                    sharedPressure = self.calculateSharedPressure(density, self.densities[sampleIndex])

                    if (density != 0):
                        pressure_force += sharedPressure * dir * self.particles[sampleIndex].mass * slope / density
            
        net_force = (self.mu * viscosity_force) + pressure_force
        return net_force

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

        volume = 15 / (np.pi * np.pow(self.smoothingDistance, 6))
        return volume * np.pow(self.smoothingDistance - dist, 3)
    
    def smoothingKernelDerivative(self, dist):
        if (dist >= self.smoothingDistance): return 0

        volume = -45 / (np.pi * np.pow(self.smoothingDistance, 6))
        return volume * np.pow(self.smoothingDistance - dist, 2)
    
    def smoothingKernelViscosity(self, dist):
        if (dist >= self.smoothingDistance): return 0

        volume = 45 / (np.pi * np.pow(self.smoothingDistance, 6))
        return volume * (self.smoothingDistance - dist)
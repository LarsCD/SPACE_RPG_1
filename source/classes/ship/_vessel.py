import time
from collections import deque

import numpy as np
import math

from numpy import floating

from source.classes.location._location import Location
from utility.tools.dev_logger import DevLogger


class Vessel:
    def __init__(self, data):
        self.logger = DevLogger(Vessel)

        # location
        self.coordinates: tuple = tuple(data['location']['coordinates'])  # world position (x, y)
        self.vector: np.ndarray = np.array((0.0, 0.0))  # velocity vector

        # info
        self.tag: str = data['info']['tag']
        self.name: str = data['info']['name']
        self.vessel_type: str = data['info']['vessel_type']
        self.description: str = data['info']['description']

        # flags
        self.is_destroyed: bool = False
        self.visible_on_radar: bool = True

        # movement properties
        self.speed: float = 0.0           # current speed (m/s)
        self.max_speed: float = 5000.0    # max speed (m/s)
        self.acceleration: float = 500  # m/s^2
        self.deceleration: float = 500  # m/s^2
        self.destination: Location | None = None
        self.orientation: float = 0.0
        self.vector: np.ndarray = np.array((0.0, 0.0))

        # effects
        self.max_trail_length = 50
        self.trail = deque()   # store (x, y, timestamp)
        self._last_trail_pos = None
        self.trail_spacing = 100.0    # min distance between trail dots
        self.trail_lifetime = 3.0     # seconds
        self.trail_speed_threshold = 1.0  # m/s, don’t emit below this

        # combat


    def __str__(self):
        return f"{self.vessel_type}__{self.tag}__{self.coordinates}"


    # --- movement methods ---


    def set_destination(self, destination):
        """Assign a world-space destination for autopilot movement."""
        if type(destination) == tuple:
            # controller chose random place on map
            self.destination = destination
        else:
            self.destination: Location = destination

    def is_stationary(self, eps=1e-2):
        return abs(self.speed) < eps

    def stop(self):
        """Immediately stop movement."""
        self.destination = None
        self.vector[:] = (0.0, 0.0)

    def get_destination_distance(self) -> floating:
        vessel_loc = np.array(self.coordinates)
        if type(self.destination) == tuple:
            destination_loc = self.destination
        else:
            destination_loc = np.array(self.destination.coordinates)

        distance = np.linalg.norm(vessel_loc - destination_loc)
        return distance


    def update(self, dt: float):
        if not self.destination:
            # decelerate to stop
            if self.speed > 0:
                self.speed -= self.deceleration * dt
                self.speed = max(self.speed, 0)
                nx, ny = self.vector / (np.linalg.norm(self.vector) + 1e-6)
                self.coordinates = (
                    self.coordinates[0] + nx * self.speed * dt,
                    self.coordinates[1] + ny * self.speed * dt
                )
            return

        if type(self.destination) == tuple:
            # vector toward destination
            dx = self.destination[0] - self.coordinates[0]
            dy = self.destination[1] - self.coordinates[1]

            distance = self.get_destination_distance()
            if distance < 1.0:  # arrival threshold
                self.coordinates = self.destination
                self.destination = None
                self.speed = 0.0
                self.vector[:] = (0.0, 0.0)
                return
        else:
            # vector toward destination
            dx = self.destination.coordinates[0] - self.coordinates[0]
            dy = self.destination.coordinates[1] - self.coordinates[1]

            distance = self.get_destination_distance()
            if distance < 1.0:  # arrival threshold
                self.coordinates = self.destination.coordinates
                self.destination = None
                self.speed = 0.0
                self.vector[:] = (0.0, 0.0)
                return

        # normalize direction
        direction = np.array([dx, dy]) / distance

        # determine whether to accelerate or decelerate
        stopping_distance = (self.speed ** 2) / (2 * self.deceleration)
        if distance > stopping_distance:
            # accelerate
            self.speed += self.acceleration * dt
            self.speed = min(self.speed, self.max_speed)
        else:
            # decelerate
            self.speed -= self.deceleration * dt
            self.speed = max(self.speed, 0)

        self.vector = direction * self.speed
        self.coordinates = (
            self.coordinates[0] + self.vector[0] * dt,
            self.coordinates[1] + self.vector[1] * dt
        )

        # update orientation
        self.orientation = math.atan2(direction[1], direction[0])


        # --- TRAIL LOGIC ---
        now = time.time()

        # purge expired points
        while self.trail and now - self.trail[0][2] > self.trail_lifetime:
            self.trail.popleft()

        # only emit if vessel is moving
        if self.speed > self.trail_speed_threshold:
            if self._last_trail_pos is None:
                self._last_trail_pos = tuple(self.coordinates)

            dx = self.coordinates[0] - self._last_trail_pos[0]
            dy = self.coordinates[1] - self._last_trail_pos[1]
            dist2 = dx*dx + dy*dy

            if dist2 >= self.trail_spacing * self.trail_spacing:
                self.trail.append((self.coordinates[0], self.coordinates[1], now))
                if len(self.trail) > self.max_trail_length:
                    self.trail.popleft()
                self._last_trail_pos = tuple(self.coordinates)

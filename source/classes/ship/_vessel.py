import numpy as np
import math


class Vessel:
    def __init__(self, data):
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

        # --- movement properties ---
        self.speed: float = 1_000.0    # meters per second (example)
        self.destination: tuple | None = None  # world-space target coords
        self.orientation: float = 0.0   # radians, optional if you later want facing



    def __str__(self):
        return f"{self.vessel_type}__{self.tag}__{self.coordinates}"



    # --- movement methods ---


    def set_destination(self, coords: tuple[float, float]):
        """Assign a world-space destination for autopilot movement."""
        self.destination = coords


    def stop(self):
        """Immediately stop movement."""
        self.destination = None
        self.vector[:] = (0.0, 0.0)


    def update(self, dt: float):
        """Advance vessel position by dt seconds toward its destination."""
        if not self.destination:
            return

        x, y = self.coordinates
        dx = self.destination[0] - x
        dy = self.destination[1] - y
        dist = math.hypot(dx, dy)

        if dist < self.speed * dt:
            # Arrive at target
            self.coordinates = self.destination
            self.destination = None
            self.vector[:] = (0.0, 0.0)
        else:
            nx, ny = dx / dist, dy / dist
            vx, vy = nx * self.speed, ny * self.speed
            self.vector[:] = (vx, vy)
            self.coordinates = (
                x + vx * dt,
                y + vy * dt,
            )

            # keep orientation consistent with movement vector
            self.orientation = math.atan2(ny, nx)

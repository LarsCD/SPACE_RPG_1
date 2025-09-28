import random
import time
from enum import Enum, auto

from source.classes.ship.ship_class import Ship


class AIState(Enum):
    IDLE = auto()
    TRAVELING = auto()
    DOCKED = auto()


class AIController(Ship):
    def __init__(self, data, world_locations, config=None):
        super().__init__(data)

        self.state = AIState.IDLE
        self.world_locations = world_locations  # all location objects in world
        self.dock_until = 0

        # config = tweakable knobs
        self.config = {
            "min_dwell_time": 5.0,
            "max_dwell_time": 15.0,
            "idle_time": 2.0,
        }
        if config:
            self.config.update(config)

        self._last_state_change = time.time()


    def update(self, dt):
        now = time.time()


        if self.state == AIState.IDLE:
            if now - self._last_state_change > self.config["idle_time"]:
                self._choose_new_destination()

        elif self.state == AIState.TRAVELING:

            # destination arrives at destination
            if self.get_destination_distance() < 25:
                self._enter_location(self.destination)

        elif self.state == AIState.DOCKED:
            if now > self.dock_until:
                self._leave_location()

    def _choose_new_destination(self):
        # check if controller has destination
        if not self.destination is None:
            return

        # choose random location to go to
        self.destination = random.choice(self.world_locations)

        self.set_destination(self.destination)
        self.state = AIState.TRAVELING
        self._last_state_change = time.time()

    def _enter_location(self, location):
        self.visible_on_radar = False
        dwell = random.uniform(
            self.config["min_dwell_time"],
            self.config["max_dwell_time"],
        )
        self.dock_until = time.time() + dwell
        location.docked_vessels.add(self)
        self.state = AIState.DOCKED
        self._last_state_change = time.time()

    def _leave_location(self):
        if self.destination:
            self.destination.docked_vessels.discard(self)

        self.visible_on_radar = True
        self.destination = None
        self.state = AIState.IDLE
        self._last_state_change = time.time()

    # --- debug helpers ---
    def debug_info(self):
        return {
            "state": self.state.name,
            "target": getattr(self.target_location, "name", None),
            "coords": tuple(round(c, 1) for c in self.coordinates),
            "destination": self.destination,
        }

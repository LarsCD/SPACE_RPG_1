import logging
from typing import Any
from xml.sax.xmlreader import Locator

import numpy as np

from source.classes.location._location import Location
from source.classes.ship._vessel import Vessel
from utility.tools.dev_logger import DevLogger


class Ship(Vessel):
    def __init__(self, data):
        super().__init__(data)
        self.log = DevLogger(Ship).log

        self.ship_type: str = data['info']['ship_type']             # type of ship (frigate, cargo, bomber, capital, etc.)

        # modules
        self.engine: dict = data['engine']
        self.fuel_cell: dict = data['fuel']
        self.hull: dict = data['hull']
        self.weapons: dict = data['weapons']
        self.sensors: dict = data['sensors']
        self.signature: dict = data['signature']


        # combat info
        self.target = None
        self.target_range: float = None
        self.target_distance: float = 0.0

        # combat flags
        self.has_target: bool = False

        # other flags
        self.is_player: bool = True


    def give_target(self, target_object):
        self.target = target_object
        self.has_target = self.check_has_target()


    def release_target(self):
        self.target = None
        self.has_target = self.check_has_target()


    def check_has_target(self):
        return self.target is not None


    def get_distance_to_target(self):
        if self.has_target:
            ship_loc = np.array(self.coordinates)
            target_loc = np.array(self.target.coordinates)

            distance = np.linalg.norm(ship_loc - target_loc)
            return distance
        else:
            return 0.0

    def get_distance_to_location_km(self, object: Any):
        ship_loc = np.array(self.coordinates)
        object_loc = np.array(object.coordinates)

        distance = np.linalg.norm(ship_loc - object_loc)
        return distance

    def get_distance_to_location_Mm(self, location: Location):
        distance = self.get_distance_to_location_km(location)
        return distance/1000
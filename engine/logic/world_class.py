from source.classes.location._location import Location
from source.classes.ship._vessel import Vessel


class World:
    def __init__(self):
        self.locations: list[Location] = []     # list of all locations in the world
        self.vessels: list[Vessel] = []         # list of all vessels in the world


    def update(self):
        # place where the updating of positions and states will be
        pass



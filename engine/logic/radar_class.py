from source.classes.location._location import Location
from source.classes.player.player import Player


class Radar_System:
    def __init__(self, radar_radius, radar_scale, radar_size):
        self.radius = radar_radius
        self.scale = radar_scale
        self.size = radar_size


    def get_blips(self, player: Player, loc_list: list[Location]):
        blips = []
        sx, sy = player.coordinates
        for location in loc_list:
            dx = location.coordinates[0] - sx
            dy = location.coordinates[1] - sy

            # remap axes (ship-centered + player orientation) and attach to object
            location.radar_dx = dy * self.scale
            location.radar_dy = -dx * self.scale

            dist = (location.radar_dx ** 2 + location.radar_dy ** 2) ** 0.5
            if dist <= self.size:
                blips.append(location)
        return blips



class Vessel:
    def __init__(self, data):
        self.coordinates: tuple = tuple(data['location']['coordinates'])  # 2d coordinate

        # info
        self.tag: str = data['info']['tag']                         # unique tag for ship (debug name)
        self.name: str = data['info']['name']                       # name of ship
        self.vessel_type: str = data['info']['vessel_type']         # type of vessel    (ship, etc.. (?))
        self.description: str = data['info']['description']         # description

        # flags
        self.is_destroyed: bool = False

    def __str__(self):
        return f"[{self.vessel_type}] \'{self.name}\' (tag=\'{self.tag}\') at {self.coordinates}"


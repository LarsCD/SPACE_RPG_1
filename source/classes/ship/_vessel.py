

class Vessel:
    def __init__(self, data):
        self.coordinates: tuple = tuple(data['location']['coordinates'])  # 2d coordinate

        # info
        self.name: str = data['info']['name']                       # name of ship
        self.tag: str = data['info']['tag']                         # unique tag for ship (debug name)
        self.location_type: str = data['info']['location_type']     # type of ship (cargo, bomber, capital, etc.)
        self.ship_type: str = data['info']['ship_type']
        self.description: str = data['info']['description']         # description

        # flags
        self.is_destroyed: bool = False
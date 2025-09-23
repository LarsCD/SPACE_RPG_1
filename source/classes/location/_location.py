

class Location:

    def __init__(self, data: dict) -> None:
        self.coordinates: tuple = tuple(data['location']['coordinates'])        # 2d coordinate
        self.location_parent_tag: str = data['location']['location_parent_tag'] # binds this location to another location as child
        self.child_locations = []

        # info
        self.name: str = data['info']['name']                       # name of location
        self.tag: str = data['info']['tag']                         # unique tag for location (debug name)
        self.location_type: str = data['info']['location_type']     # type of location (station, asteroid, etc.)
        self.description: str = data['info']['description']         # description

        # flags
        self.is_hidden: bool = data['flags']['is_hidden']           # is location hidden to player


    def __str__(self):
        return f"[{self.location_type}] \'{self.name}\' (tag=\'{self.tag}\') at {self.coordinates}"


    def update_location(self, coordinates: tuple) -> None:
        """
        Updates coordinates of location

        :param coordinates:
        :return:
        """
        self.coordinates = coordinates


    def hide_from_player(self) -> None:
        """
        Hides location from player

        :return:
        """
        self.is_hidden = True


    def unhide_from_player(self) -> None:
        """
        Un-hides location to player

        :return:
        """
        self.is_hidden = False


    @staticmethod
    def add_child_location(self, location_object):
        """
        Make location object child of this location object, adds to children list

        :param self:
        :param location_object:
        :return:
        """
        self.child_locations.append(location_object)




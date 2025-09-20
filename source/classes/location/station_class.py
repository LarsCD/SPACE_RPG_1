from source.classes.location._location import Location

class Station(Location):

    def __init__(self, data: dict) -> None:
        super().__init__(data)  # initialize params from Module class

        self.station_type = data["info"]["station_type"]
        self.station_services = data['functions']['services']


from source.classes.location._location import Location

class Station(Location):

    def __init__(self, data: dict) -> None:
        super().__init__(data)  # initialize params from Module class

        self.station_type = data["info"]["station_type"]
        self.station_services = data['functions']['services']

        self.faction: str = data['info']['faction']
        self.level_requirement: int = data['info']['level_requirement']


    def check_has_service(self, service: str) -> bool:
        return service in self.station_services


    def check_has_level_req(self, player_level) -> bool:
        return player_level <= self.level_requirement
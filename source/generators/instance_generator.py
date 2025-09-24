from source.classes.location._location import Location
from source.classes.location.station_class import Station


class Instance_Generator:
    def __init__(self):
        pass

    @staticmethod
    def generate_all_locations(game_data: dict) -> list[Location]:
        locations_data_list: dict = game_data['stations']['station_data_generated']['game']
        location_object_list: list[Location] = []

        for location in locations_data_list:
            location_data = locations_data_list[location]

            # if location is Station
            if location_data['info']['location_type'] == 'station':
                location_object = Station(location_data)
                location_object_list.append(location_object)

        return location_object_list

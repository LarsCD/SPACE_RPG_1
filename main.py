from source.generators.instance_generator import Instance_Generator
from utility.tools.dataloader import Dataloader
from source.classes.location.station_class import Station
from source.classes.ship.ship_class import Ship

def main() -> None:
    data_loader = Dataloader()
    data = data_loader.load_data()
    print(data)
    station_object = Station(data['stations']['station_data']['debug']['debug_station_01'])
    print(station_object)
    ship_object = Ship(data['ships']['ship_data']['debug']['debug_ship_01'])
    print(ship_object)

    list = Instance_Generator.generate_all_locations(data)
    print(list)
    

if __name__ == "__main__":
    main()
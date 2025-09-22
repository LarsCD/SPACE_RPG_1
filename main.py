from utility.tools.dataloader import Dataloader
from source.classes.location.station_class import Station
from source.classes.ship._vessel import Vessel

def main() -> None:
    data_loader = Dataloader()
    data = data_loader.load_data()
    print(data)
    station_object = Station(data['stations']['station_data']['debug']['debug_station_01'])
    print(station_object)

if __name__ == "__main__":
    main()
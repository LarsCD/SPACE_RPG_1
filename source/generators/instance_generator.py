# engine/generators/instance_generator.py
# updated to produce Location (stations) and Vessel/Ship objects from loaded data.

from typing import List, Dict
from source.classes.location._location import Location
from source.classes.location.station_class import Station
from source.classes.ship.ship_class import Ship  # your Ship implementation


class Instance_Generator:
    @staticmethod
    def generate_all_locations(game_data: dict) -> List[Location]:
        """
        Reads station definitions from the dataset and returns a list of Location objects.
        Supports the structure: game_data['stations']['station_data_generated']['game']
        """
        locations = []
        stations_section = None

        # try common key patterns
        if "stations" in game_data and "station_data_generated" in game_data["stations"]:
            stations_section = game_data["stations"]["station_data_generated"].get("game", {})
        elif "station_data_generated" in game_data:
            stations_section = game_data["station_data_generated"].get("game", {})
        else:
            stations_section = game_data.get("stations", {}).get("station_data_generated", {}).get("game", {})

        for key, loc_data in stations_section.items():
            if loc_data.get("info", {}).get("location_type") == "station":
                locations.append(Station(loc_data))
            else:
                locations.append(Location(loc_data))
        return locations

    @staticmethod
    def generate_all_vessels(game_data: dict) -> List[Ship]:
        """
        Reads ship definitions and returns Ship objects.
        Supports structure: game_data['ships']['ship_data_generated']['game'] or game_data['ships']['game'] or top-level 'game'.
        """
        vessels = []

        # possible locations for ship definitions (backwards-compatible)
        candidates = [
            ("ships", "ship_data_generated", "game"),
            ("ships", "game"),
            (None, "game"),  # top-level "game" as in the snippet you showed
        ]

        ship_entries = {}
        for path in candidates:
            if path[0] is None:
                # top-level 'game' (as your provided file showed)
                ship_entries = game_data.get("game", {})
            else:
                cursor = game_data.get(path[0], {})
                for p in path[1:]:
                    if isinstance(cursor, dict):
                        cursor = cursor.get(p, {})
                if isinstance(cursor, dict):
                    ship_entries = cursor
            if ship_entries:
                break

        # instantiate Ship objects
        for key, ship_data in ship_entries.items():
            try:
                vessels.append(Ship(ship_data))
            except Exception:
                # skip malformed entries defensively
                continue

        return vessels

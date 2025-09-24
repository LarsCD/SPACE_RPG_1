# engine/managers/world_manager.py
from utility.tools.dataloader import Dataloader
from source.generators.instance_generator import Instance_Generator
from source.classes.player.player import Player
from typing import Tuple, List
from source.classes.ship.ship_class import Ship
import copy

class WorldManager:
    """Load world, locations, vessels, and player. Ensures sample ships exist on map."""

    def __init__(self):
        self.data = None
        self.locations = []
        self.vessels = []
        self.player = None

    def load(self) -> Tuple[List, List, Player]:
        self.data = Dataloader().load_data()

        # locations (stations, asteroids, etc.)
        self.locations = Instance_Generator.generate_all_locations(self.data)

        # vessels (NPC ships + ship definitions)
        self.vessels = Instance_Generator.generate_all_vessels(self.data)

        # ensure a few sample ships exist; if not, clone debug ship into several positions
        if not self.vessels or len(self.vessels) < 3:
            debug_ship = self.data.get('debug', {}).get('debug_ship_01') or self.data.get('ships', {}).get('ship_data', {}).get('debug', {}).get('debug_ship_01')
            if debug_ship:
                sample_positions = [(1200.0, 450.5), (3400.0, 1700.5), (500.5, 1200.2)]
                for i, pos in enumerate(sample_positions):
                    clone = copy.deepcopy(debug_ship)
                    clone['info']['tag'] = f"sample_ship_{i}"
                    clone['info']['name'] = f"Sample Ship {i}"
                    clone['location']['coordinates'] = [pos[0], pos[1]]
                    try:
                        self.vessels.append(Ship(clone))
                    except Exception:
                        pass

        # player creation (prefer explicit debug slot if present)
        player_data = None
        try:
            player_data = self.data['ships']['ship_data']['debug']['debug_ship_01']
        except Exception:
            # fallback: use first vessel data if available
            if self.vessels:
                # construct minimal player_data from vessel data
                v = self.vessels[0]
                player_data = {
                    "info": {
                        "tag": "player_ship",
                        "name": "Player Ship",
                        "vessel_type": "ship",
                        "ship_type": getattr(v, "ship_type", "frigate"),
                        "description": "Auto-generated player ship"
                    },
                    "location": {"coordinates": [0.0, 0.0]},
                    "engine": {},
                    "fuel": {},
                    "hull": {},
                    "weapons": {},
                    "sensors": {},
                    "signature": {}
                }

        self.player = Player(player_data)
        return self.locations, self.vessels, self.player

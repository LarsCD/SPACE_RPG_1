# engine/managers/world_manager.py
import random
from typing import Tuple, List
import copy

from utility.tools.dataloader import Dataloader
from source.generators.instance_generator import Instance_Generator
from source.classes.player.player import Player
from source.classes.ship.ship_class import Ship
from source.classes.AI.AI_controller import AIController
from utility.tools.dev_logger import DevLogger


class WorldManager:
    """Load world, locations, vessels, and player. Ensures NPC ships are AI-controlled."""
    def __init__(self):
        self.logger = DevLogger(WorldManager)

        self.data = None
        self.locations = []
        self.vessels: List = []
        self.player: Player | None = None

        self.SHIP_SPAWN_TABLE = {
            "scout_01": 5,
            "freighter_omega": 2,
            "corsair_07": 3,
        }
        self.SHIP_SPAWN_RANGE = {
            'x': [-4000, 4000],
            'y': [-4000, 4000]
        }


    def load(self) -> Tuple[List, List, Player]:
        self.data = Dataloader().load_data()

        # --- locations ---
        self.locations = Instance_Generator.generate_all_locations(self.data)

        # --- vessels from "game" data ---
        vessels: List = []
        # spawn what type
        for ship_name in self.SHIP_SPAWN_TABLE:
            # spawn how many?
            for _ in range(self.SHIP_SPAWN_TABLE[ship_name]):
                spawn_vessel = AIController(copy.deepcopy(self.data['ships']['ship_data']['game'][ship_name]), self.locations)


                # generate random spawn position
                spawn_coordinates = (
                    random.randrange(self.SHIP_SPAWN_RANGE['x'][0], self.SHIP_SPAWN_RANGE['x'][1]),
                    random.randrange(self.SHIP_SPAWN_RANGE['y'][0], self.SHIP_SPAWN_RANGE['y'][1])
                )

                spawn_vessel.coordinates = spawn_coordinates
                self.logger.info(f"spawning {spawn_vessel} at {spawn_coordinates}")
                vessels.append(spawn_vessel)


        self.vessels = vessels

        # --- player creation ---
        player_data = self.data['ships']['ship_data']['debug'].get('debug_ship_01')
        if not player_data:
            if self.vessels:
                fallback = copy.deepcopy(self.vessels[0].raw_data) if hasattr(self.vessels[0], "raw_data") else None
                if fallback:
                    fallback["info"]["tag"] = "player_ship"
                    fallback["info"]["name"] = "Player Ship"
                    player_data = fallback
            if not player_data:
                raise RuntimeError("No suitable ship data found for player.")

        self.player = Player(copy.deepcopy(player_data))

        # --- return all world objects ---
        return self.locations, self.vessels, self.player

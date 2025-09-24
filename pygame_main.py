import pygame
from data.config.config_settings import GAME_DEFAULTS
from engine.core.game_core import Game

if __name__ == "__main__":
    pygame.init()
    pygame.font.init()
    Game().run()

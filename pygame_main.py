# framework
import pygame

# config files
from data.config.config_settings import GAME_DEFAULTS

# data and classes
from source.generators.instance_generator import Instance_Generator
from source.classes.player.player import Player
from utility.tools.dataloader import Dataloader

# logic and rendering
from engine.logic.world_class import World
from engine.logic.radar_class import Radar_System
from engine.logic.radar_interaction import RadarInteraction
from engine.renderers.radar_renderer import RadarRenderer
from engine.renderers.panel_renderer import PanelRenderer


# ============== PYGAME SETUP ==============
pygame.init()
pygame.font.init()

# Set up the game window
SCREEN_SIZE = (1600, 1000)
screen = pygame.display.set_mode(SCREEN_SIZE)
pygame.display.set_caption(GAME_DEFAULTS['game_name'])


# --- helper functions ---
def mouse_to_world(mouse_x, mouse_y, radar_center, player, scale):
    """
    Convert a mouse position in radar-space to world coordinates.
    Up = +x, Right = +y, consistent with radar coordinate remap.
    """
    cx, cy = radar_center
    dx = mouse_x - cx
    dy = mouse_y - cy

    # invert radar-space transform
    world_dx = -dy / scale
    world_dy = dx / scale

    px, py = player.coordinates
    return px + world_dx, py + world_dy


# --- main start ---
def main_start():
    data = Dataloader().load_data()
    loc_list = Instance_Generator.generate_all_locations(data)
    player = Player(data['ships']['ship_data']['debug']['debug_ship_01'])

    radar_radius = 5000
    radar_scale = 0.1
    radar_size = 400
    render_label_scale = radar_scale

    main_loop(loc_list, player, radar_radius, radar_scale, radar_size, render_label_scale)


# --- main loop ---
def main_loop(loc_list, player, radar_radius, radar_scale, radar_size, render_label_scale):
    clock = pygame.time.Clock()
    running = True

    radar_center = (SCREEN_SIZE[0] // 2, SCREEN_SIZE[1] // 2)

    # initialize radar system and renderer
    radar_system = Radar_System(radar_radius, radar_scale, radar_size)
    radar_renderer = RadarRenderer(screen, radar_center, radar_radius, radar_scale, radar_size)
    radar_interaction = RadarInteraction(radar_center, radar_size)

    # initialize panel renderer (right side of screen)
    panel_rect = pygame.Rect(SCREEN_SIZE[0] - 300, 0, 300, SCREEN_SIZE[1])
    panel_renderer = PanelRenderer(screen, panel_rect)

    # sync scale
    radar_renderer.scale = radar_scale
    radar_renderer.label_scale = render_label_scale

    player.target = loc_list[4]

    while running:
        dt = clock.tick(60) / 1000  # seconds per frame

        # --- update ---
        player.update(dt)

        # --- radar blips ---
        blips = radar_system.get_blips(player, loc_list)

        # --- event handling ---
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            selection = radar_interaction.handle_event(event, blips)
            if selection:
                player.give_target(selection)

            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    radar_scale += 0.005
                    render_label_scale -= 0.005
                elif event.key == pygame.K_DOWN:
                    radar_scale -= 0.005
                    render_label_scale += 0.005

                # update scale
                radar_system.scale = radar_scale
                radar_renderer.scale = radar_scale
                radar_renderer.label_scale = render_label_scale

            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                # left click → move player vessel
                dest = mouse_to_world(event.pos[0], event.pos[1],
                                      radar_renderer.center,
                                      player,
                                      radar_system.scale)
                player.set_destination(dest)

        # --- drawing ---
        screen.fill((20, 20, 20))
        radar_renderer.draw(blips, player)
        panel_renderer.draw(player)  # draws player stats + target info + buttons
        pygame.display.flip()

    pygame.quit()


if __name__ == "__main__":
    main_start()

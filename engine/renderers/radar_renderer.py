import pygame
from pygame.examples.arraydemo import surfdemo_show

from source.classes.player.player import Player


class RadarRenderer:
    def __init__(self, surface, center, radar_radius, radar_scale, radar_size) :
        self.surface = surface
        self.center = center
        self.radius = radar_radius
        self.scale = radar_scale
        self.label_scale = 0.0
        self.size = radar_size

    def draw(self, blips, player: Player):
        font = pygame.font.SysFont(None, 24)

        # radar outline
        pygame.draw.circle(self.surface, (0, 100, 0), self.center, self.size, 2)

        # world range at outer ring (Mm) = radius in pixels / pixels-per-Mm
        max_range = (self.size / self.scale) / 1000

        rings = 5
        for i in range(1, rings + 1):
            frac = i / rings

            # pixel radius
            radius = int(self.size * frac)

            # world distance at this radius
            world_dist = round((radius / self.scale) / 1000, 1)


            # draw circle
            pygame.draw.circle(self.surface, (0, 60, 0), self.center, radius, 1)

            # draw label
            label = font.render(f"{world_dist} Mm", True, (0, 200, 0))
            self.surface.blit(label, (self.center[0] + radius, self.center[1] - 10))

        mouse_x, mouse_y = pygame.mouse.get_pos()

        for location in blips:
            cx, cy = self.center
            x, y = cx + location.radar_dx, cy + location.radar_dy

            # draw blip
            pygame.draw.circle(self.surface, (0, 255, 0), (int(x), int(y)), 4)

            # hover detection
            if (mouse_x - x) ** 2 + (mouse_y - y) ** 2 <= 36:
                dist = round(player.get_distance_to_location_Mm(location), 1)

                info = [
                    f"{location.name}",
                    f"Type: {location.location_type}",
                    f"{dist} Mm"
                ]

                for i, text in enumerate(info):
                    label = font.render(text, True, (0, 255, 0))
                    self.surface.blit(label, (x + 25, y - 15 + i * 20))


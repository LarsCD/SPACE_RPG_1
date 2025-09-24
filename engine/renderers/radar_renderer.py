import pygame
from source.classes.player.player import Player


class RadarRenderer:
    def __init__(self, surface, center, radar_radius, radar_scale, radar_size):
        self.surface = surface
        self.center = center
        self.radius = radar_radius
        self.scale = radar_scale
        self.size = radar_size

    def draw(self, blips, player: Player):
        font = pygame.font.SysFont(None, 24)

        # radar outline
        pygame.draw.circle(self.surface, (0, 100, 0), self.center, self.size, 2)

        # draw range rings
        rings = 5
        for i in range(1, rings + 1):
            frac = i / rings
            radius = int(self.size * frac)
            world_dist = round((radius / self.scale) / 1000, 1)

            pygame.draw.circle(self.surface, (0, 60, 0), self.center, radius, 1)

            label = font.render(f"{world_dist} Mm", True, (0, 200, 0))
            self.surface.blit(label, (self.center[0] + radius, self.center[1] - 10))

        mouse_x, mouse_y = pygame.mouse.get_pos()

        # draw blips
        for location in blips:
            cx, cy = self.center
            x, y = cx + location.radar_dx, cy + location.radar_dy

            # blip
            pygame.draw.circle(self.surface, (0, 255, 0), (int(x), int(y)), 4)

            # hover info
            if (mouse_x - x) ** 2 + (mouse_y - y) ** 2 <= 36:
                dist = round(player.get_distance_to_location_Mm(location), 1)
                info = [f"{location.name}", f"Type: {location.location_type}", f"{dist} Mm"]

                for i, text in enumerate(info):
                    label = font.render(text, True, (0, 255, 0))
                    self.surface.blit(label, (x + 25, y - 15 + i * 20))

            # draw target diamond
            if player.target is location:
                size = 15
                x_offset = -1
                y_offset = 1
                points = [
                    (x+x_offset, y - size-y_offset),
                    (x+x_offset + size, y-y_offset),
                    (x+x_offset, y + size-y_offset),
                    (x+x_offset - size, y-y_offset)
                ]
                pygame.draw.polygon(self.surface, (0, 255, 0), points, 2)

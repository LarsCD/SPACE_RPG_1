import pygame


class RadarInteraction:
    def __init__(self, center, radar_size):
        self.center = center
        self.size = radar_size
        self.selected = None

    def handle_event(self, event, blips):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            mx, my = pygame.mouse.get_pos()
            cx, cy = self.center

            for location in blips:
                x, y = cx + location.radar_dx, cy + location.radar_dy
                if (mx - x) ** 2 + (my - y) ** 2 <= 36:
                    self.selected = location
                    return location

        return None

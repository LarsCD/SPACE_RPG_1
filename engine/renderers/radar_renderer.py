import time

import pygame

from source.classes.location._location import Location
from source.classes.player.player import Player
from source.classes.ship._vessel import Vessel
from source.classes.ship.ship_class import Ship

# --- Colors ---
BLIP_COLOR = (0, 255, 0)
RING_COLOR = (0, 60, 0)
OUTLINE_COLOR = (0, 100, 0)
SELECTED_COLOR = (0, 255, 0)
LOCKED_TRIANGLE_COLOR = (255, 200, 0)
DEST_RING_COLOR = (200, 200, 0)
PLAYER_BLIP_COLOR = (0, 200, 255)


class RadarRenderer:
    """
    Draws radar with:
      - outline and range rings
      - blips (locations as dots, vessels as triangles)
      - selected diamond
      - locked inverted triangle for vessels
      - destination marker (doughnut shape)
    """

    def __init__(self, surface, center: tuple[int, int], radar_radius_pix: int, radar_scale: float, radar_size: int):
        self.surface = surface
        self.center = center
        self.radar_radius = radar_radius_pix   # world units, for reference
        self.scale = radar_scale               # world units -> pixels
        self.size = radar_size                 # visual pixel radius
        self.label_scale = radar_scale         # alias for compatibility
        self.font = pygame.font.SysFont(None, 20)


    # --- Utility Methods ---
    def is_inside(self, pos: tuple[int, int]) -> bool:
        """Check if a position is within the radar circle."""
        mx, my = pos
        cx, cy = self.center
        return (mx - cx) ** 2 + (my - cy) ** 2 <= self.size ** 2

    def world_to_radar(self, world_pos: tuple[float, float], ship) -> tuple[float, float]:
        """
        Convert world coordinates to radar-space coordinates relative to the ship.

        Axis mapping:
            Up = +x, Right = +y → radar_dx = dy, radar_dy = -dx
        """
        sx, sy = ship.coordinates
        dx = world_pos[0] - sx
        dy = world_pos[1] - sy
        return dy * self.scale, -dx * self.scale


    # --- Drawing Methods ---
    def draw(self, blips: list, player, selected=None, locked=None, destination_marker=None):
        """
        Draw radar, blips, selection indicators, locked indicators, and optional destination.

        :param blips: list of objects with coordinates or radar_dx/radar_dy
        :param player: player object for reference coordinates
        :param selected: currently selected object (diamond)
        :param locked: currently locked object (inverted triangle)
        :param destination_marker: dict with keys {'active': bool, 'coords': (x,y)}
        """


        cx, cy = self.center

        self._draw_outline_and_rings(cx, cy, self.font, player)
        self._draw_destination_marker(cx, cy, destination_marker, player)
        self._draw_blips(cx, cy, blips, player, selected, locked)


    # --- Internal drawing helpers ---
    def _draw_outline_and_rings(self, cx, cy, font, player):
        pygame.draw.circle(self.surface, OUTLINE_COLOR, (int(cx), int(cy)), self.size, 2)

        rings = 4
        for i in range(1, rings + 1):
            r_px = int(self.size * (i / (rings + 1)))
            pygame.draw.circle(self.surface, RING_COLOR, (int(cx), int(cy)), r_px, 1)
            # Draw world distance in Mm
            world_dist_mm = (r_px / self.scale / 1000, 1)

            unit_prefix = "Mm"
            dist_label = 0.0
            if world_dist_mm[0] < 1:
                unit_prefix = "km"
                dist_label = round(world_dist_mm[0] * 1000, 2)
            else:
                dist_label = round(world_dist_mm[0])

            label = font.render(f"{dist_label} {unit_prefix}", True, BLIP_COLOR)
            self.surface.blit(label, (cx + r_px + 6, cy - 10))


    def _draw_destination_marker(self, cx, cy, destination_marker, player):
        if destination_marker and destination_marker.get("active") and destination_marker.get("coords"):
            rdx, rdy = self.world_to_radar(destination_marker["coords"], player)
            dx_px, dy_px = int(cx + rdx), int(cy + rdy)
            outer, inner = 12, 3
            pygame.draw.circle(self.surface, DEST_RING_COLOR, (dx_px, dy_px), outer, 2)
            pygame.draw.circle(self.surface, DEST_RING_COLOR, (dx_px, dy_px), inner, 0)


    def _draw_blips(self, cx, cy, blips, player, selected, locked):
        for obj in blips:
            # dont draw vessel if vessel is invisible
            if isinstance(obj, Vessel) and not getattr(obj, "visible_on_radar", True):
                continue

            rdx = getattr(obj, "radar_dx", None)
            rdy = getattr(obj, "radar_dy", None)
            if rdx is None or rdy is None:
                rdx, rdy = self.world_to_radar(obj.coordinates, player)

            x_px, y_px = int(cx + rdx), int(cy + rdy)

            # Draw vessel/location
            if issubclass(type(obj), Vessel):
                self._draw_vessel_blip(x_px, y_px, obj, player)
                self._draw_trail(obj)
            elif issubclass(type(obj), Location):
                self._draw_location_blip(x_px, y_px)

            # Draw selected diamond
            if selected is obj:
                self._draw_diamond(x_px, y_px)

            # Draw locked inverted triangle
            if locked is obj:
                self._draw_locked_triangle(x_px, y_px)


        # draw player
        self._draw_player_blip()
        self._draw_trail(player)


    def _draw_trail(self, vessel: Vessel | Player):
        if not hasattr(vessel, "trail") or not vessel.trail:
            return

        cx, cy = self.center
        now = time.time()

        for x, y, t in vessel.trail:
            age = now - t
            fade = max(0, 1.0 - age / vessel.trail_lifetime)  # 1→0 over lifetime
            if fade <= 0:
                continue

            # world → radar transform relative to player
            rdx, rdy = self.world_to_radar((x, y), vessel)
            rx, ry = int(cx + rdx), int(cy + rdy)

            # faded green color
            color = (0, int(255 * fade), 0)

            pygame.draw.circle(self.surface, color, (rx, ry), 2)



    # --- Small shape render helpers ---
    def _draw_vessel_blip(self, x_px, y_px, vessel: Vessel, player: Player):
        size = 4
        points = [(x_px, y_px - size), (x_px - size, y_px + size), (x_px + size, y_px + size)]

        pygame.draw.polygon(self.surface, BLIP_COLOR, points)


        dist = player.get_distance_to_location_Mm(vessel)
        unit_prefix = "Mm"
        dist_label = 0.0
        if dist < 1:
            unit_prefix = "km"
            dist_label = round(dist * 1000)
        else:
            dist_label = round(dist)

        id_label = self.font.render(f"id:      {vessel.tag}", True, BLIP_COLOR)
        state_label = self.font.render(f"dist: {dist_label} {unit_prefix}", True, BLIP_COLOR)

        self.surface.blit(id_label, (x_px+25, y_px-25))
        self.surface.blit(state_label, (x_px + 25, y_px - 5))

    def _draw_location_blip(self, x_px, y_px):
        size = 6
        pygame.draw.circle(self.surface, BLIP_COLOR, (x_px, y_px), size)

    def _draw_player_blip(self):
        x_px, y_px = int(self.center[0]), int(self.center[1])
        size = 6
        points = [(x_px, y_px - size), (x_px - size, y_px + size), (x_px + size, y_px + size)]
        pygame.draw.polygon(self.surface, PLAYER_BLIP_COLOR, points)

    def _draw_diamond(self, x, y):
        s = 14
        x_offset = 0
        y_offset = 1
        diamond = [(x + x_offset, y - s - y_offset), (x + s + x_offset, y - y_offset), (x + x_offset, y + s - y_offset), (x - s + x_offset, y - y_offset)]
        pygame.draw.polygon(self.surface, SELECTED_COLOR, diamond, 3)

    def _draw_locked_triangle(self, x, y):
        size = 14
        y_offset = 2
        points = [(x - size, y - size + y_offset), (x + size, y - size + y_offset), (x, y + size + y_offset)]
        pygame.draw.polygon(self.surface, LOCKED_TRIANGLE_COLOR, points, 3)

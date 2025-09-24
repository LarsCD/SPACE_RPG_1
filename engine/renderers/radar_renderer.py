import pygame
import math

# drawing constants
BLIP_COLOR = (0, 255, 0)
RING_COLOR = (0, 60, 0)
OUTLINE_COLOR = (0, 100, 0)
SELECTED_COLOR = (0, 255, 0)
LOCKED_TRIANGLE_COLOR = (255, 200, 0)  # visually distinct
DEST_RING_COLOR = (200, 200, 0)


class RadarRenderer:
    """
    Draws radar, blips, destination marker doughnut, selected diamond, and locked inverted triangle.
    """

    def __init__(self, surface, center: tuple[int, int], radar_radius_pix: int, radar_scale, radar_size):
        self.surface = surface
        self.center = center
        # radius in world units (not used for drawing)
        self.radar_radius = radar_radius_pix
        # scale: world-units -> pixels
        self.scale = radar_scale
        # visual pixel radius (size)
        self.size = radar_size
        # alias used earlier code
        self.label_scale = radar_scale

        # daughter attributes for outside control
        self.destination = {"active": False, "coords": None}

    def is_inside(self, pos):
        mx, my = pos
        cx, cy = self.center
        return (mx - cx) ** 2 + (my - cy) ** 2 <= self.size * self.size

    def world_to_radar(self, world_pos, ship):
        """Return (radar_dx_px, radar_dy_px) given world coords and ship coords using your axis mapping."""
        sx, sy = ship.coordinates
        dx = world_pos[0] - sx
        dy = world_pos[1] - sy
        # remap as established: Up = +x, Right = +y → radar_dx = dy, radar_dy = -dx
        radar_dx = dy * self.scale
        radar_dy = -dx * self.scale
        return radar_dx, radar_dy

    def draw(self, blips, player, selected=None, locked=None, destination_marker=None):
        """
        blips: list of location/vessel objects with .radar_dx/.radar_dy already computed or use world_to_radar()
        selected: object currently selected (diamond)
        locked: locked object (inverted triangle)
        destination_marker: dict {'active':bool, 'coords':(x,y)}
        """
        font = pygame.font.SysFont(None, 20)
        cx, cy = self.center

        # radar outline + rings
        pygame.draw.circle(self.surface, OUTLINE_COLOR, (int(cx), int(cy)), self.size, 2)
        rings = 4
        for i in range(1, rings + 1):
            r_px = int(self.size * (i / (rings + 1)))
            pygame.draw.circle(self.surface, RING_COLOR, (int(cx), int(cy)), r_px, 1)
            # label world distance in Mm
            world_dist_mm = round((r_px / self.scale) / 1000, 1)
            label = font.render(f"{world_dist_mm} Mm", True, BLIP_COLOR)
            self.surface.blit(label, (cx + r_px + 6, cy - 10))

        # draw destination doughnut if requested
        if destination_marker and destination_marker.get("active") and destination_marker.get("coords"):
            dest_world = destination_marker["coords"]
            rdx, rdy = self.world_to_radar(dest_world, player)
            dx_px = int(cx + rdx)
            dy_px = int(cy + rdy)
            outer = 12
            inner = 6
            pygame.draw.circle(self.surface, DEST_RING_COLOR, (dx_px, dy_px), outer, 2)  # outer ring
            pygame.draw.circle(self.surface, DEST_RING_COLOR, (dx_px, dy_px), inner, 0)  # filled center

        # draw blips
        for obj in blips:
            # if radar system already set radar_dx/dy on objects, use them. Otherwise compute from world coords.
            rdx = getattr(obj, "radar_dx", None)
            rdy = getattr(obj, "radar_dy", None)
            if rdx is None or rdy is None:
                rdx, rdy = self.world_to_radar(obj.coordinates, player)

            x_px = int(cx + rdx)
            y_px = int(cy + rdy)

            # draw the blip: vessel -> triangle, location -> dot
            if hasattr(obj, "vessel_type"):
                # triangle pointing up (default). fill small triangle
                size = 6
                points = [(x_px, y_px - size), (x_px - size, y_px + size), (x_px + size, y_px + size)]
                pygame.draw.polygon(self.surface, BLIP_COLOR, points)
            else:
                pygame.draw.circle(self.surface, BLIP_COLOR, (x_px, y_px), 4)

            # draw selected diamond
            if selected is obj:
                s = 10
                diamond = [(x_px, y_px - s), (x_px + s, y_px), (x_px, y_px + s), (x_px - s, y_px)]
                pygame.draw.polygon(self.surface, SELECTED_COLOR, diamond, 1)

            # draw locked inverted triangle (upside-down) for locked vessels
            if locked is obj:
                size = 12
                points = [
                    (x_px - size, y_px - size),  # top-left
                    (x_px + size, y_px - size),  # top-right
                    (x_px, y_px + size),         # bottom (inverted)
                ]
                pygame.draw.polygon(self.surface, LOCKED_TRIANGLE_COLOR, points, 2)

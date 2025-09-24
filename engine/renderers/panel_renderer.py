# engine/renderers/panel_renderer.py
import pygame
from source.classes.ship._vessel import Vessel
from source.classes.ship.ship_class import Ship
from source.classes.location._location import Location
from source.classes.location.station_class import Station


class PanelRenderer:
    def __init__(self, surface, rect: pygame.Rect):
        self.surface = surface
        self.rect = rect
        self.font = pygame.font.SysFont(None, 24)

        # buttons are stored as {label: (rect, callback)}
        self.buttons: dict[str, tuple[pygame.Rect, callable]] = {}

    def draw(self, player):
        pygame.draw.rect(self.surface, (10, 10, 10), self.rect)
        pygame.draw.rect(self.surface, (0, 100, 0), self.rect, 2)

        y = self.rect.top + 10
        lines = [
            f"Player: {player.name}",
            f"Coords: {tuple(int(c) for c in player.coordinates)}",
        ]
        for line in lines:
            label = self.font.render(line, True, (0, 255, 0))
            self.surface.blit(label, (self.rect.left + 10, y))
            y += 30

        self.buttons.clear()

        if player.has_target:
            target = player.target
            y += 20
            y = self._draw_target_info(player, target, y)
            y += 20
            y = self._draw_target_buttons(player, target, y)

    def _draw_target_info(self, player, target, y):
        if isinstance(target, Ship):
            return self._draw_ship_info(player, target, y)
        elif isinstance(target, Vessel):
            return self._draw_vessel_info(player, target, y)
        elif isinstance(target, Station):
            return self._draw_station_info(player, target, y)
        elif isinstance(target, Location):
            return self._draw_location_info(player, target, y)
        return y

    def _draw_ship_info(self, player, ship: Ship, y):
        lines = [
            f"Target: {ship.name}",
            f"Class: {ship.ship_type}",
            f"Distance: {round(player.get_distance_to_location_Mm(ship), 1)} Mm",
        ]
        return self._render_lines(lines, y)

    def _draw_vessel_info(self, player, vessel: Vessel, y):
        lines = [
            f"Target: {vessel.name}",
            f"Type: {vessel.vessel_type}",
            f"Distance: {round(player.get_distance_to_location_Mm(vessel), 1)} Mm",
        ]
        return self._render_lines(lines, y)

    def _draw_station_info(self, player, station: Station, y):
        services = ", ".join(station.station_services)
        lines = [
            f"Target: {station.name}",
            f"Station Type: {station.station_type}",
            f"Faction: {station.faction}",
            f"Services: {services}",
            f"Distance: {round(player.get_distance_to_location_Mm(station), 1)} Mm",
        ]
        return self._render_lines(lines, y)

    def _draw_location_info(self, player, loc: Location, y):
        lines = [
            f"Target: {loc.name}",
            f"Type: {loc.location_type}",
            f"Distance: {round(player.get_distance_to_location_Mm(loc), 1)} Mm",
        ]
        return self._render_lines(lines, y)

    def _draw_target_buttons(self, player, target, y):
        # Ship → show attack and hail
        if isinstance(target, Ship):
            y = self._render_button("Attack", y, lambda: print(f"Attack {target.name}"))
            y = self._render_button("Hail", y, lambda: print(f"Hail {target.name}"))

        # Station → show dock and trade
        elif isinstance(target, Station):
            y = self._render_button("Dock", y, lambda: print(f"Dock at {target.name}"))
            y = self._render_button("Trade", y, lambda: print(f"Trade with {target.name}"))

        # Location → show set course
        elif isinstance(target, Location):
            y = self._render_button("Set Course", y, lambda: print(f"Set course to {target.name}"))

        return y

    def _render_lines(self, lines, y):
        for line in lines:
            label = self.font.render(str(line), True, (0, 255, 0))
            self.surface.blit(label, (self.rect.left + 10, y))
            y += 30
        return y

    def _render_button(self, label: str, y: int, callback: callable) -> int:
        rect = pygame.Rect(self.rect.left + 10, y, self.rect.width - 20, 30)
        pygame.draw.rect(self.surface, (0, 60, 0), rect)
        pygame.draw.rect(self.surface, (0, 200, 0), rect, 2)

        text = self.font.render(label, True, (0, 255, 0))
        self.surface.blit(text, (rect.x + 10, rect.y + 5))

        self.buttons[label] = (rect, callback)
        return y + 40

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            mx, my = event.pos
            for label, (rect, callback) in self.buttons.items():
                if rect.collidepoint(mx, my):
                    callback()

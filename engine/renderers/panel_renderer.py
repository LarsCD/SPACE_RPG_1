# engine/renderers/panel_renderer.py
import pygame
from typing import Callable

from source.classes.AI.AI_controller import AIController

BG = (10, 10, 10)
BORDER = (0, 100, 0)
TEXT = (0, 255, 0)
BTN_BG = (0, 60, 0)
BTN_BORDER = (0, 200, 0)
BTN_DISABLED_BG = (60, 0, 0)
BTN_DISABLED_BORDER = (150, 0, 0)
RED = (200, 40, 40)


class PanelRenderer:
    """
    PanelRenderer supports dynamic rendering of:
      - player info
      - selected-target info (right panel)
      - locked-target info (left panel)
      - pending destination preview + Confirm/Cancel buttons
      - debug data for ships and locations
    """

    def __init__(self, surface: pygame.Surface, rect: pygame.Rect, side: str = "right"):
        self.surface = surface
        self.rect = pygame.Rect(rect)
        self.side = side
        self.font = pygame.font.SysFont(None, 20)
        self.actions: dict[str, Callable] = {}
        self._buttons: dict[str, tuple[pygame.Rect, bool]] = {}

    def register_action(self, label: str, callback: Callable):
        self.actions[label] = callback

    def draw(self, player, selected=None, locked=None, pending_destination=None):
        pygame.draw.rect(self.surface, BG, self.rect)
        pygame.draw.rect(self.surface, BORDER, self.rect, 2)

        y = self.rect.top + 10
        left = self.rect.left + 10

        # player header
        lines = [
            f"Player: {player.name}",
            f"Coords: {tuple(int(c) for c in player.coordinates)}",
            f"Speed:  {round(player.speed, 1)} m/s",
            f"- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -"
        ]
        for l in lines:
            self.surface.blit(self.font.render(l, True, TEXT), (left, y))
            y += 22

        # pending destination info + Confirm/Cancel buttons
        if pending_destination and pending_destination.get("active") and self.side == "right":
            y = self._draw_pending_destination(pending_destination, left, y)

        # selected target info (right panel)
        if selected and self.side == "right":
            y += 6
            y = self._draw_target_info(selected, player, left, y)

        # locked target info (left panel)
        if locked and self.side == "left":
            y += 6
            y = self._draw_target_info(locked, player, left, y)

    def _draw_pending_destination(self, pending, left, y):
        coords = pending.get("coords")
        self.surface.blit(
            self.font.render(f"Pending dest: {tuple(round(c,1) for c in coords)}", True, TEXT),
            (left, y),
        )
        y += 30

        self._buttons.clear()
        confirm_rect = pygame.Rect(left, y, self.rect.width - 20, 32)
        pygame.draw.rect(self.surface, BTN_BG, confirm_rect)
        pygame.draw.rect(self.surface, BTN_BORDER, confirm_rect, 2)
        self.surface.blit(
            self.font.render("Confirm Move", True, TEXT), (confirm_rect.x + 8, confirm_rect.y + 6)
        )
        self._buttons["Confirm Move"] = (confirm_rect, True)
        y += 40

        cancel_rect = pygame.Rect(left, y, self.rect.width - 20, 32)
        pygame.draw.rect(self.surface, BTN_DISABLED_BG, cancel_rect)
        pygame.draw.rect(self.surface, BTN_DISABLED_BORDER, cancel_rect, 2)
        self.surface.blit(
            self.font.render("Cancel Move", True, RED), (cancel_rect.x + 8, cancel_rect.y + 6)
        )
        self._buttons["Cancel Move"] = (cancel_rect, True)
        y += 44
        return y

    def _draw_target_info(self, target, player, left_x, start_y):
        y = start_y
        name = getattr(target, "name", getattr(target, "tag", "Unknown"))
        ttype = getattr(target, "vessel_type", getattr(target, "location_type", "Unknown"))


        unit_prefix = "Mm"
        dist_label = 0.0
        dist_mm = player.get_distance_to_location_Mm(target)
        if dist_mm < 1:
            unit_prefix = "km"
            dist_label = round(player.get_distance_to_location_Mm(target)*1000, 1)
        else:
            dist_label = round(dist_mm)

        # lines = [f"Target: {name}", f"Type: {ttype}", f"Distance: {dist_mm} Mm"]
        # for line in lines:
        #     self.surface.blit(self.font.render(line, True, TEXT), (left_x, y))
        #     y += 22

        # --- Debug info for vessels ---
        if type(target) == AIController:
            target: AIController = target
            lines = [f"Target: {target.name} ({target.tag})", f"Type: {target.ship_type}", f"Distance: {dist_label} {unit_prefix}", f"AI State: {target.state.name}", f"Destination: {target.destination}"]
            for line in lines:
                self.surface.blit(self.font.render(line, True, TEXT), (left_x, y))
                y += 22

        # --- Debug info for locations ---
        if hasattr(target, "docked_vessels"):
            info = target.debug_info()
            self.surface.blit(
                self.font.render(f"Docked ships: {len(info['docked'])}", True, TEXT),
                (left_x, y),
            )
            y += 20
            for vname in info["docked"]:
                self.surface.blit(self.font.render(f" - {vname}", True, TEXT), (left_x + 10, y))
                y += 18

        # Example: Dock button for stations
        if getattr(target, "__class__", None).__name__ == "Station":
            can_dock = dist_mm <= 0.5
            label = "Dock"
            rect = pygame.Rect(left_x, y, self.rect.width - 20, 32)
            bg = BTN_BG if can_dock else BTN_DISABLED_BG
            border = BTN_BORDER if can_dock else BTN_DISABLED_BORDER
            pygame.draw.rect(self.surface, bg, rect)
            pygame.draw.rect(self.surface, border, rect, 2)
            txtcol = TEXT if can_dock else RED
            self.surface.blit(self.font.render(label, True, txtcol), (rect.x + 8, rect.y + 6))
            self._buttons[label] = (rect, can_dock)
            y += 40

        # vessel lock and travel buttons
        if hasattr(target, "vessel_type"):
            rect = pygame.Rect(left_x, y, self.rect.width - 20, 32)
            pygame.draw.rect(self.surface, BTN_BG, rect)
            pygame.draw.rect(self.surface, BTN_BORDER, rect, 2)
            self.surface.blit(self.font.render("Lock", True, TEXT), (rect.x + 8, rect.y + 6))
            self._buttons["Lock"] = (rect, True)
            y += 40

            rect = pygame.Rect(left_x, y, self.rect.width - 20, 32)
            pygame.draw.rect(self.surface, BTN_BG, rect)
            pygame.draw.rect(self.surface, BTN_BORDER, rect, 2)
            self.surface.blit(self.font.render("Travel", True, TEXT), (rect.x + 8, rect.y + 6))
            self._buttons["Travel"] = (rect, True)
            y += 40

        return y

    def handle_event(self, event) -> bool:
        if event.type != pygame.MOUSEBUTTONDOWN or event.button != 1:
            return False

        mx, my = event.pos
        for label, (rect, enabled) in list(self._buttons.items()):
            if rect.collidepoint(mx, my) and enabled:
                cb = self.actions.get(label)
                if cb:
                    cb()
                return True
        return False

# engine/input/input_manager.py
import pygame
from typing import Iterable
from engine.core.tools import mouse_to_world

HIT_RADIUS_PX = 6
HIT_RADIUS_SQ = HIT_RADIUS_PX * HIT_RADIUS_PX


class InputManager:
    """
    Handles all user inputs:
      - keyboard zoom
      - left-click inside radar: select blip or set pending destination (preview)
      - left-click outside radar: set pending destination (preview)
      - exposes selected, locked_target and pending_destination
    """

    def __init__(self, radar_renderer, radar_system, player):
        self.radar_renderer = radar_renderer
        self.radar_system = radar_system
        self.player = player

        self.render_scale = radar_system.scale
        self.render_label_scale = radar_renderer.label_scale

        # selection state
        self.selected = None
        self.locked_target = None

        # pending destination (requires user confirmation)
        # {"active": bool, "coords": (x,y), "screen_pos": (mx,my)}
        self.pending_destination: dict = {"active": False, "coords": None, "screen_pos": None}

    def inside_radar(self, pos: tuple[int, int]) -> bool:
        mx, my = pos
        cx, cy = self.radar_renderer.center
        r = self.radar_renderer.size
        return (mx - cx) ** 2 + (my - cy) ** 2 <= r * r

    def handle_event(self, event: pygame.event.Event, blip_object_list: Iterable):
        # keyboard
        if event.type == pygame.KEYDOWN:
            self._handle_keyboard(event)

        # left mouse button
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.inside_radar(event.pos):
                self._handle_radar_click(event.pos, blip_object_list)
            else:
                self._handle_world_click(event.pos)

        # right-click clears pending destination
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 3:
            self.pending_destination["active"] = False
            self.pending_destination["coords"] = None
            self.pending_destination["screen_pos"] = None

        # return selected object if any (some callers expect this)
        return getattr(self, "_last_selection", None)

    # ----- keyboard handlers -----
    def _handle_keyboard(self, event: pygame.event.Event):
        if not hasattr(event, "key"):
            return
        if event.key == pygame.K_UP:
            self.render_scale += 0.005
            self.render_label_scale = max(0.0001, self.render_label_scale - 0.005)
        elif event.key == pygame.K_DOWN:
            self.render_scale = max(0.001, self.render_scale - 0.005)
            self.render_label_scale += 0.005

        # sync values
        self.radar_system.scale = self.render_scale
        self.radar_renderer.scale = self.render_scale
        self.radar_renderer.label_scale = self.render_label_scale

    # ----- radar click handling -----
    def _handle_radar_click(self, pos: tuple[int, int], blip_object_list: Iterable):
        mx, my = pos
        cx, cy = self.radar_renderer.center

        clicked_on_blip = False
        self._last_selection = None

        for obj in blip_object_list:
            bx, by = cx + getattr(obj, "radar_dx", 0), cy + getattr(obj, "radar_dy", 0)
            if (mx - bx) ** 2 + (my - by) ** 2 <= HIT_RADIUS_SQ:
                clicked_on_blip = True
                self.selected = obj
                self._last_selection = obj
                # prepare pending destination to object's world coordinates (preview)
                self.pending_destination["active"] = True
                self.pending_destination["coords"] = tuple(obj.coordinates)
                # store approximate screen position for UI (used by panel or overlays)
                self.pending_destination["screen_pos"] = (bx, by)
                return

        # if not clicking a blip: set pending destination to clicked radar point (convert to world)
        dest_world = mouse_to_world(mx, my, self.radar_renderer.center, self.player, self.radar_system.scale)
        self.pending_destination["active"] = True
        self.pending_destination["coords"] = tuple(dest_world)
        self.pending_destination["screen_pos"] = (mx, my)
        self._last_selection = None

    # ----- outside radar world click (screen space) -----
    def _handle_world_click(self, pos: tuple[int, int]):
        # clicking outside radar simply sets a pending destination (world coords from mouse)
        dest_world = mouse_to_world(pos[0], pos[1], self.radar_renderer.center, self.player, self.radar_system.scale)
        self.pending_destination["active"] = True
        self.pending_destination["coords"] = tuple(dest_world)
        self.pending_destination["screen_pos"] = pos
        self._last_selection = None

    # ----- locking -----
    def toggle_lock(self):
        if self.locked_target is None and self.selected is not None:
            # only lock objects that look like vessels
            if hasattr(self.selected, "vessel_type"):
                self.locked_target = self.selected
        else:
            self.locked_target = None

    def confirm_move(self):
        """Commit pending destination to player's autopilot."""
        if not self.pending_destination.get("active"):
            return False
        coords = self.pending_destination.get("coords")
        if coords is None:
            return False
        self.player.set_destination(tuple(coords))
        # keep a destination_marker separate if radar renderer uses different structure
        self.pending_destination["active"] = False
        return True

    def cancel_move(self):
        self.pending_destination["active"] = False
        self.pending_destination["coords"] = None
        self.pending_destination["screen_pos"] = None

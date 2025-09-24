# engine/core/game_core.py
"""
Game core orchestration.

- Minimal, well-structured main loop
- Uses InputManager for all input (keyboard, radar clicks, world clicks)
- RadarSystem computes blips
- RadarRenderer draws radar + blips + selection/lock/destination markers
- PanelRenderer draws left/right panels and handles panel button clicks

Drop this file into engine/core/ and import Game from your entrypoint.
"""

from __future__ import annotations

import pygame
from typing import Iterable, Optional

from engine.managers.world_manager import WorldManager
from engine.input.input_manager import InputManager
from engine.logic.radar_class import Radar_System
from engine.renderers.radar_renderer import RadarRenderer
from engine.renderers.panel_renderer import PanelRenderer
from source.classes.location._location import Location
from source.classes.ship._vessel import Vessel
from source.classes.player.player import Player


class Game:
    """Main game orchestrator. Keep run() small and declarative."""

    def __init__(self, screen_size: tuple[int, int] = (1600, 1000)):
        pygame.init()
        pygame.font.init()

        self.screen_size = screen_size
        self.screen = pygame.display.set_mode(screen_size)
        pygame.display.set_caption("SPACE RPG 1")

        # --- world & player ---
        self.world_manager = WorldManager()
        self.locations, self.vessels, self.player = self.world_manager.load()

        # --- radar configuration ---
        self.center = (screen_size[0] // 2, screen_size[1] // 2)
        self.radar_radius = 5000     # logical (world) radius if used elsewhere
        self.radar_scale = 0.1       # world units -> pixels
        self.label_scale = 0.1
        self.radar_size = 450        # visual radius in pixels

        self.radar_system = Radar_System(self.radar_radius, self.radar_scale, self.radar_size)
        self.radar_renderer = RadarRenderer(
            surface=self.screen,
            center=self.center,
            radar_radius_pix=self.radar_radius,
            radar_scale=self.radar_scale,
            radar_size=self.radar_size
        )

        # Input manager handles keyboard + mouse (radar + world)
        self.input_manager = InputManager(self.radar_renderer, self.radar_system, self.player)

        # Panels
        right_panel_rect = (self.center[0] + self.radar_size + 50, 50, 400, 600)
        left_panel_rect = (40, 50, 340, 600)
        self.right_panel = PanelRenderer(self.screen, right_panel_rect, side="right")
        self.left_panel = PanelRenderer(self.screen, left_panel_rect, side="left")

        # register panel actions that call Game methods
        self.right_panel.register_action("Confirm Move", self._confirm_move)
        self.right_panel.register_action("Cancel Move", self._cancel_move)
        self.right_panel.register_action("Travel", self._travel_to_selected)
        self.right_panel.register_action("Dock", self._dock_to_selected)
        self.right_panel.register_action("Lock", self._toggle_lock)

        # debug: sample default target (remove later)
        if self.locations:
            self.player.target = self.locations[4]

        # runtime
        self.clock = pygame.time.Clock()
        self.running = True



    # -------------------------
    # Game action helpers
    # -------------------------
    def _travel_to_selected(self):
        sel = self.input_manager.selected
        if not sel:
            return
        # prepare a pending destination (preview) — requires confirmation in panel
        self.input_manager.pending_destination["active"] = True
        self.input_manager.pending_destination["coords"] = tuple(sel.coordinates)
        self.input_manager.pending_destination["screen_pos"] = None

    def _dock_to_selected(self):
        sel = self.input_manager.selected
        if not sel:
            return
        # docking flow placeholder
        # implement dock sequence here
        print(f"[Game] Dock action requested for {getattr(sel, 'name', sel)}")

    def _toggle_lock(self):
        self.input_manager.toggle_lock()

    def _confirm_move(self):
        moved = self.input_manager.confirm_move()
        if moved:
            # pending_destination cleared by InputManager.confirm_move()
            # no extra state required here
            return True
        return False

    def _cancel_move(self):
        self.input_manager.cancel_move()

    # -------------------------
    # Main loop
    # -------------------------
    def run(self):
        while self.running:
            dt = self.clock.tick(60) / 1000.0

            # --- update simulation ---
            # update player and vessels (vessel.update should move them if they have destinations)
            self.player.update(dt)
            for v in self.vessels:
                v.update(dt)

            # --- radar blips ---
            # compute blips for locations (and optionally vessels)
            # radar_system.get_blips expects player and a list of Location-like objects
            blips: list[Location | Vessel] = []
            # include locations and vessels as blippable objects
            blips.extend(self.radar_system.get_blips(self.player, self.locations))
            # for vessels, convert to same interface (if you want them on radar)
            # NOTE: Radar_System.get_blips mutates objects with radar_dx/radar_dy
            if self.vessels:
                vessel_blips = self.radar_system.get_blips(self.player, self.vessels)
                blips.extend(vessel_blips)

            # --- event handling ---
            # engine/core/game_core.py (inside Game.run)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                    break

                # let panels consume clicks first (they return True if they handled the event)
                panel_consumed = self.right_panel.handle_event(event) or self.left_panel.handle_event(event)
                if panel_consumed:
                    # panel click handled — do not pass event to InputManager
                    continue

                # otherwise let input manager handle keyboard/radar/world clicks
                selection = self.input_manager.handle_event(event, blips)
                if selection:
                    # selection may already have set player.target inside InputManager
                    self.player.give_target(selection)

                # Panels handle their own button click detection
                self.right_panel.handle_event(event)
                self.left_panel.handle_event(event)

            # --- drawing ---
            self.screen.fill((20, 20, 20))

            self.radar_renderer.draw(
                blips,
                self.player,
                selected=self.input_manager.selected,
                locked=self.input_manager.locked_target,
                destination_marker=self.input_manager.pending_destination
            )

            self.right_panel.draw(
                self.player,
                selected=self.input_manager.selected,
                locked=self.input_manager.locked_target,
                pending_destination=self.input_manager.pending_destination
            )

            self.left_panel.draw(
                self.player,
                selected=self.input_manager.selected,
                locked=self.input_manager.locked_target,
                pending_destination=self.input_manager.pending_destination
            )

            pygame.display.flip()

        pygame.quit()

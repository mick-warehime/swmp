import unittest

import pygame

import mods
import settings
from test.pygame_mock import initialize_pygame
from view import dungeon_view


def setUpModule() -> None:
    initialize_pygame()


class ViewTest(unittest.TestCase):
    def setUp(self) -> None:
        screen = pygame.display.set_mode((settings.WIDTH, settings.HEIGHT))
        self.view = dungeon_view.DungeonView()

    def test_click_mod(self) -> None:
        locs = [m for m in mods.ModLocation]
        for idx, loc in enumerate(self.view._hud.mod_rects):
            r = self.view._hud.mod_rects[loc]
            x = r.centerx
            y = r.centery
            self.view.try_click_hud((x, y))
            self.assertEqual(self.view.selected_mod(), locs[idx])

        # ensure previous loop gets hit
        self.assertTrue(idx > 0)

        self.view.try_click_hud((0, 0))
        self.assertEqual(self.view.selected_mod(), -1)

    def test_click_item(self) -> None:
        for idx, r in enumerate(self.view._hud.backpack_rects):
            x = r.centerx
            y = r.centery
            self.view.try_click_hud((x, y))
            self.assertEqual(self.view.selected_item(), idx)

        # ensure previous loop gets hit
        self.assertTrue(idx > 0)

        self.view.try_click_hud((0, 0))
        self.assertEqual(self.view.selected_item(), -1)

    def test_click_twice_reset(self) -> None:
        r = self.view._hud.backpack_rects[0]
        x = r.centerx
        y = r.centery
        self.view.try_click_hud((x, y))
        self.assertEqual(self.view.selected_item(), 0)
        self.view.try_click_hud((x, y))
        self.assertEqual(self.view.selected_item(), -1)

    def test_click_backpack_when_hidden(self) -> None:
        r = self.view._hud.backpack_rects[0]
        x = r.centerx
        y = r.centery
        self.assertFalse(self.view.hud_collide_point((x, y)))

        self.view.toggle_hide_backpack()

        self.assertTrue(self.view.hud_collide_point((x, y)))

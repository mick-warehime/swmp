import unittest
from typing import Union
import os
from unittest.mock import Mock

from pygame.math import Vector2
import pygame

import controller
import model
import humanoids as hmn
from dungeon_controller import DungeonController
from mods import PistolObject, ShotgunObject, HealthPackObject
from src.test.pygame_mock import MockTimer, Pygame, initialize_pygame, \
    initialize_gameobjects

from test import pygame_mock
from view import DungeonView

pg = pygame_mock.Pygame()
controller.pg.mouse = pg.mouse
controller.pg.key = pg.key

# This allows for running tests without actually generating a screen display
# or audio output.
os.environ['SDL_VIDEODRIVER'] = 'dummy'
os.environ['SDL_AUDIODRIVER'] = 'dummy'

pg = Pygame()


def _make_player() -> hmn.Player:
    pos = pygame.math.Vector2(0, 0)
    player = hmn.Player(pos)
    return player


def _make_mob(player: Union[hmn.Player, None] = None,
              pos: Union[Vector2, None] = None) -> hmn.Mob:
    if player is None:
        player = _make_player()
    if pos is None:
        pos = player.pos + pygame.math.Vector2(100, 0)
    return hmn.Mob(pos, player, is_quest=False)


def setUpModule() -> None:
    initialize_pygame()
    level = 'test_level.tmx'
    blank_screen = pygame.Surface((800, 600))
    DungeonControllerTest.dng_ctrl = DungeonController(blank_screen, level)


def _make_dungeon_controller() -> DungeonController:
    level = 'test_level.tmx'
    blank_screen = pygame.Surface((800, 600))
    return DungeonController(blank_screen, level)


class DungeonControllerTest(unittest.TestCase):

    def tearDown(self) -> None:
        pass

    def test_health_pack_in_backpack_does_not_prevent_equip(self) -> None:
        dng_ctrl = _make_dungeon_controller()
        player = dng_ctrl.player

        pos = Vector2(0, 0)
        pistol = PistolObject(pos)
        shotgun = ShotgunObject(pos)

        player.attempt_pickup(pistol)
        player.attempt_pickup(shotgun)  # shotgun mod goes to slot 0 in backpack
        player.attempt_pickup(HealthPackObject(pos))
        player.attempt_pickup(HealthPackObject(pos))

        mock_view = Mock(spec=DungeonView)

        mock_view.selected_item = lambda: 0
        dng_ctrl._view = mock_view

        pistol_mod = pistol.mod
        shotgun_mod = shotgun.mod
        weapon_loc = pistol_mod.loc
        self.assertEqual(player.active_mods[weapon_loc], pistol_mod)
        dng_ctrl.equip_mod_in_backpack()
        self.assertEqual(player.active_mods[weapon_loc], shotgun_mod)


if __name__ == '__main__':
    unittest.main()
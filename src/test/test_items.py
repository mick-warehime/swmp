import os
import unittest

import pygame

import humanoid as hmn
import mod
import model
import settings
from item_manager import ItemManager
from test.pygame_mock import initialize_pygame, initialize_gameobjects, \
    MockTimer

# This allows for running tests without actually generating a screen display
# or audio output.
os.environ['SDL_VIDEODRIVER'] = 'dummy'
os.environ['SDL_AUDIODRIVER'] = 'dummy'


class Connection(object):
    groups = model.Groups()
    timer = MockTimer()


def setUpModule() -> None:
    initialize_pygame()
    initialize_gameobjects(Connection.groups, Connection.timer)


def _make_player() -> hmn.Player:
    groups = Connection.groups
    pos = pygame.math.Vector2(0, 0)
    player = hmn.Player(pos)
    player.set_weapon('pistol')
    return player


def _make_item(label: str) -> model.Item:
    pos = (0, 0)
    groups = Connection.groups
    return ItemManager.item(groups, pos, label)


class ModTest(unittest.TestCase):
    def tearDown(self) -> None:
        groups = Connection.groups
        groups.walls.empty()
        groups.mobs.empty()
        groups.bullets.empty()
        groups.all_sprites.empty()
        groups.items.empty()

        Connection.timer.reset()

    def test_add_items(self) -> None:
        player = _make_player()
        hp = _make_item(settings.HEALTHPACK_ITEM)

        self.assertEqual(len(player.backpack), 0)

        for i in range(player.backpack_size):
            player.add_item_to_backpack(hp)
            self.assertEqual(len(player.backpack), i + 1)

        self.assertTrue(player.backpack_full())

    def test_use_health_pack(self) -> None:
        player = _make_player()
        hp = _make_item(settings.HEALTHPACK_ITEM)

        self.assertEqual(len(player.backpack), 0)

        player.add_item_to_backpack(hp)

        # health is full
        self.assertFalse(player.damaged)

        hp.use(player)

        # health pack doesn't work if health is full
        self.assertFalse(player.damaged)
        self.assertEqual(len(player.backpack), 1)

        player.increment_health(-settings.HEALTH_PACK_AMOUNT)
        self.assertTrue(player.damaged)
        hp.use(player)

        # health pack fills health back up and is gone from backpack
        self.assertFalse(player.damaged)
        self.assertEqual(len(player.backpack), 0)

        player.add_item_to_backpack(hp)
        player.increment_health(-1)

        hp.use(player)

        # health pack doesn't fill you over max health
        self.assertEqual(player.health, settings.PLAYER_HEALTH)
        self.assertEqual(len(player.backpack), 0)

    def test_add_mod(self) -> None:
        player = _make_player()
        shotgun = _make_item(settings.SHOTGUN_MOD)

        player.add_item_to_backpack(shotgun)

        # nothing installed at arms location -> install shotgun
        self.assertEqual(len(player.backpack), 0)
        arm_mod = player.active_mods[mod.ModLocation.ARMS]
        self.assertEqual(arm_mod, shotgun)

        # adding a second arm mod goes into the backpack
        pistol = _make_item(settings.PISTOL_MOD)

        player.add_item_to_backpack(pistol)
        self.assertEqual(len(player.backpack), 1)
        arm_mod = player.active_mods[mod.ModLocation.ARMS]
        self.assertEqual(arm_mod, shotgun)
        self.assertIn(pistol, player.backpack)

        # make sure we can swap the pistol with the shotgun
        pistol.use(player)
        self.assertEqual(len(player.backpack), 1)
        arm_mod = player.active_mods[mod.ModLocation.ARMS]
        self.assertEqual(arm_mod, pistol)
        self.assertIn(shotgun, player.backpack)


if __name__ == '__main__':
    unittest.main()

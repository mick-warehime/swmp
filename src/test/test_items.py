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
    pos = pygame.math.Vector2(0, 0)
    player = hmn.Player(pos)
    player.set_weapon('pistol')
    return player


def _make_item(label: str) -> mod.ItemObject:
    pos = (0, 0)
    return ItemManager.item(pos, label)


class ModTest(unittest.TestCase):
    def tearDown(self) -> None:
        groups = Connection.groups
        groups.walls.empty()
        groups.mobs.empty()
        groups.bullets.empty()
        groups.all_sprites.empty()
        groups.items.empty()

        Connection.timer.reset()

    def test_backpack_full(self) -> None:
        player = _make_player()
        hp = _make_item(settings.HEALTHPACK)

        # TODO (dvirk): You should not be able to add the same object to the
        # backpack more than once.
        for i in range(player.backpack_size):
            self.assertFalse(player.backpack_full)
            player.gain_item(hp)
            self.assertEqual(len(player.backpack), i + 1)
        self.assertEqual(len(player.backpack), player.backpack_size)
        self.assertTrue(player.backpack_full)

        # Item not gained since backpack full
        player.gain_item(hp)
        self.assertEqual(len(player.backpack), player.backpack_size)

    def test_use_health_pack(self) -> None:
        player = _make_player()
        hp = _make_item(settings.HEALTHPACK)

        self.assertEqual(len(player.backpack), 0)

        player.gain_item(hp)

        self.assertIn(hp.mod, player.backpack)

        # health is full
        self.assertFalse(player.damaged)

        self.assertFalse(hp.mod.expended)
        hp.mod.use(player)
        self.assertFalse(hp.mod.expended)

        # health pack doesn't work if health is full
        self.assertIn(hp.mod, player.backpack)

        # health pack fills health back up and is gone from backpack
        player.increment_health(-settings.HEALTH_PACK_AMOUNT)
        self.assertTrue(player.damaged)
        hp.mod.use(player)
        self.assertTrue(hp.mod.expended)
        self.assertNotIn(hp.mod, player.backpack)
        self.assertFalse(player.damaged)
        self.assertEqual(len(player.backpack), 0)

        hp = _make_item(settings.HEALTHPACK)
        player.gain_item(hp)
        player.increment_health(-1)

        hp.mod.use(player)

        # health pack doesn't fill you over max health
        self.assertEqual(player.health, settings.PLAYER_HEALTH)
        self.assertEqual(len(player.backpack), 0)

    def test_add_weapons(self) -> None:
        player = _make_player()
        shotgun = _make_item(settings.SHOTGUN)

        player.gain_item(shotgun)

        self.assertTrue(shotgun.mod.equipable)
        # nothing installed at arms location -> install shotgun
        self.assertEqual(len(player.backpack), 0)
        arm_mod = player.active_mods[mod.ModLocation.ARMS]
        self.assertIs(arm_mod, shotgun.mod)

        # adding a second arm mod goes into the backpack
        pistol = _make_item(settings.PISTOL)

        player.gain_item(pistol)
        self.assertEqual(len(player.backpack), 1)
        arm_mod = player.active_mods[mod.ModLocation.ARMS]
        self.assertEqual(arm_mod, shotgun.mod)
        self.assertIn(pistol.mod, player.backpack)

        # make sure we can swap the pistol with the shotgun
        pistol.mod.use(player)
        self.assertEqual(len(player.backpack), 1)
        arm_mod = player.active_mods[mod.ModLocation.ARMS]
        self.assertEqual(arm_mod, pistol.mod)
        self.assertIn(shotgun.mod, player.backpack)


if __name__ == '__main__':
    unittest.main()

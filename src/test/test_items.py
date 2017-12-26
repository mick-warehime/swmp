import os
import unittest

import pygame
from pygame.math import Vector2

import humanoids as hmn
import model
import mods
from items.item_manager import ItemManager
from items.rocks import RockObject
from test.pygame_mock import initialize_pygame, initialize_gameobjects, \
    MockTimer
# This allows for running tests without actually generating a screen display
# or audio output.
from tilemap import ObjectType

os.environ['SDL_VIDEODRIVER'] = 'dummy'
os.environ['SDL_AUDIODRIVER'] = 'dummy'


def setUpModule() -> None:
    initialize_pygame()
    initialize_gameobjects(ModTest.groups, ModTest.timer)


def _make_player() -> hmn.Player:
    pos = pygame.math.Vector2(0, 0)
    player = hmn.Player(pos)
    return player


def _make_item(label: str) -> mods.ItemObject:
    pos = Vector2(0, 0)
    return ItemManager.item(pos, label)


class ModTest(unittest.TestCase):
    groups = model.Groups()
    timer = MockTimer()

    def tearDown(self) -> None:
        self.groups.empty()
        self.timer.reset()

    def test_make_item_in_groups(self) -> None:
        groups = self.groups

        hp = _make_item(ObjectType.HEALTHPACK)
        self.assertIn(hp, groups.all_sprites)
        self.assertIn(hp, groups.items)
        self.assertEqual(len(groups.all_sprites), 1)
        self.assertEqual(len(groups.items), 1)

        pistol = _make_item(ObjectType.PISTOL)
        self.assertIn(pistol, groups.all_sprites)
        self.assertIn(pistol, groups.items)
        self.assertEqual(len(groups.all_sprites), 2)
        self.assertEqual(len(groups.items), 2)

        shotgun = _make_item(ObjectType.SHOTGUN)
        self.assertIn(shotgun, groups.all_sprites)
        self.assertIn(shotgun, groups.items)
        self.assertEqual(len(groups.all_sprites), 3)
        self.assertEqual(len(groups.items), 3)

    def test_backpack_full(self) -> None:
        player = _make_player()
        pistol = _make_item(ObjectType.PISTOL)

        backpack = player.backpack
        self.assertEqual(len(backpack), player.backpack.size)
        # TODO (dvirk): You should not be able to add the same object to the
        # backpack more than once.

        for i in range(player.backpack.size + 1):
            self.assertFalse(player.backpack.is_full)
            player.attempt_pickup(pistol)
        self.assertTrue(player.backpack.is_full)

        # Item not gained since backpack full
        player.attempt_pickup(pistol)
        self.assertEqual(len(backpack), player.backpack.size)

    def test_use_health_pack(self) -> None:
        player = _make_player()
        hp = _make_item(ObjectType.HEALTHPACK)

        backpack = player.backpack

        player.attempt_pickup(hp)
        # healthpack goes straight to active mods.
        self.assertNotIn(hp.mod, backpack)  # healthpack added to stack.
        active_mods = player.active_mods
        self.assertIn(hp.mod, active_mods.values())

        hp_2 = _make_item(ObjectType.HEALTHPACK)
        player.attempt_pickup(hp_2)

        self.assertNotIn(hp_2.mod, backpack)

        # health is full
        self.assertFalse(player.damaged)

        self.assertFalse(hp.mod.expended)
        use_hp_mod = player.ability_caller(hp.mod.loc)
        use_hp_mod()
        self.assertFalse(hp.mod.expended)

        # health pack doesn't work if health is full
        self.assertIn(hp.mod, active_mods.values())

        # health pack fills health back up and is gone from active_mods
        player.increment_health(-mods.HEALTH_PACK_AMOUNT)
        self.assertTrue(player.damaged)

        # Ability is only usable after sufficient time has elapsed.
        self.timer.current_time += hp.mod.ability._cool_down + 1
        use_hp_mod = player.ability_caller(hp.mod.loc)
        use_hp_mod()

        self.assertFalse(hp.mod.expended)
        self.assertEqual(hp.mod.ability.uses_left, 1)
        self.assertNotIn(hp.mod, backpack)
        self.assertFalse(player.damaged)

        hp = _make_item(ObjectType.HEALTHPACK)
        player.attempt_pickup(hp)
        player.increment_health(-1)

        self.timer.current_time += hp.mod.ability._cool_down + 1
        use_hp_mod = player.ability_caller(hp.mod.loc)
        use_hp_mod()

        # health pack doesn't fill you over max health
        self.assertEqual(player.health, player.max_health)

    def test_add_weapons(self) -> None:
        player = _make_player()
        shotgun = _make_item(ObjectType.SHOTGUN)

        player.attempt_pickup(shotgun)

        # nothing installed at arms location -> install shotgun
        backpack = player.backpack
        self.assertNotIn(shotgun.mod, backpack)
        active_mods = player.active_mods
        arm_mod = active_mods[mods.ModLocation.ARMS]
        self.assertIs(arm_mod, shotgun.mod)

        # adding a second arm mod goes into the backpack
        pistol = _make_item(ObjectType.PISTOL)

        player.attempt_pickup(pistol)
        self.assertIn(pistol.mod, backpack)
        arm_mod = active_mods[mods.ModLocation.ARMS]
        self.assertIs(arm_mod, shotgun.mod)
        self.assertIn(pistol.mod, backpack)

        # make sure we can swap the pistol with the shotgun
        player.equip(pistol.mod)
        arm_mod = active_mods[mods.ModLocation.ARMS]
        self.assertEqual(arm_mod, pistol.mod)
        self.assertIn(shotgun.mod, backpack)

    def test_mod_stacking_in_active_mods(self):
        player = _make_player()
        pos = Vector2(0, 0)
        hp = mods.HealthPackObject(pos)

        self.assertNotIn(hp.mod.loc, player.active_mods)

        player.attempt_pickup(hp)
        player_mod = player.active_mods[hp.mod.loc]
        self.assertIs(player_mod, hp.mod)
        self.assertEqual(player_mod.ability.uses_left, 1)

        player.attempt_pickup(mods.HealthPackObject(pos))
        player_mod = player.active_mods[hp.mod.loc]
        self.assertEqual(player_mod.ability.uses_left, 2)

        player.attempt_pickup(mods.HealthPackObject(pos))
        player_mod = player.active_mods[hp.mod.loc]
        self.assertEqual(player_mod.ability.uses_left, 3)

    def test_mod_stacking_in_backpack(self):
        player = _make_player()
        pos = Vector2(0, 0)

        player.attempt_pickup(mods.PistolObject(pos))

        self.assertFalse(player.backpack.slot_occupied(0))

        player.attempt_pickup(RockObject(pos))
        self.assertTrue(player.backpack.slot_occupied(0))
        self.assertEqual(player.backpack[0].ability.uses_left, 1)

        player.attempt_pickup(RockObject(pos))
        self.assertEqual(player.backpack[0].ability.uses_left, 2)

        player.attempt_pickup(RockObject(pos))
        self.assertEqual(player.backpack[0].ability.uses_left, 3)

        player.attempt_pickup(RockObject(pos))
        self.assertEqual(player.backpack[0].ability.uses_left, 4)


if __name__ == '__main__':
    unittest.main()

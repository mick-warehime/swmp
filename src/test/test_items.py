import os
import unittest
import pygame
import humanoids as hmn
import mods
import model
from item_manager import ItemManager
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
    pos = (0, 0)
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
        hp = _make_item(ObjectType.HEALTHPACK)

        # TODO (dvirk): You should not be able to add the same object to the
        # backpack more than once.
        for i in range(player.backpack_size + 1):
            self.assertFalse(player.backpack_full)
            player.attempt_pickup(hp)
            self.assertEqual(len(player.backpack), i)
        self.assertEqual(len(player.backpack), player.backpack_size)
        self.assertTrue(player.backpack_full)

        # Item not gained since backpack full
        player.attempt_pickup(hp)
        self.assertEqual(len(player.backpack), player.backpack_size)

    def test_use_health_pack(self) -> None:
        player = _make_player()
        hp = _make_item(ObjectType.HEALTHPACK)

        self.assertEqual(len(player.backpack), 0)

        player.attempt_pickup(hp)
        # healthpack goes straight to active mods.
        self.assertNotIn(hp.mod, player.backpack)
        self.assertIn(hp.mod, player.active_mods.values())

        hp_2 = _make_item(ObjectType.HEALTHPACK)
        player.attempt_pickup(hp_2)
        self.assertIn(hp_2.mod, player.backpack)

        # health is full
        self.assertFalse(player.damaged)

        self.assertFalse(hp.mod.expended)
        use_hp_mod = player.ability_caller(hp.mod.loc)
        use_hp_mod()
        self.assertFalse(hp.mod.expended)

        # health pack doesn't work if health is full
        self.assertIn(hp.mod, player.active_mods.values())

        # health pack fills health back up and is gone from active_mods
        player.increment_health(-mods.HEALTH_PACK_AMOUNT)
        self.assertTrue(player.damaged)

        # Ability is only usable after sufficient time has elapsed.
        self.timer.current_time += hp.mod.ability._cool_down + 1
        use_hp_mod = player.ability_caller(hp.mod.loc)
        use_hp_mod()

        self.assertTrue(hp.mod.expended)
        self.assertNotIn(hp.mod, player.backpack)
        self.assertFalse(player.damaged)
        self.assertEqual(len(player.active_mods.values()), 0)

        hp = _make_item(ObjectType.HEALTHPACK)
        player.attempt_pickup(hp)
        player.increment_health(-1)

        self.timer.current_time += hp.mod.ability._cool_down + 1
        use_hp_mod = player.ability_caller(hp.mod.loc)
        use_hp_mod()

        # health pack doesn't fill you over max health
        self.assertEqual(player.health, player.max_health)
        self.assertEqual(len(player.active_mods.values()), 0)

    def test_add_weapons(self) -> None:
        player = _make_player()
        shotgun = _make_item(ObjectType.SHOTGUN)

        player.attempt_pickup(shotgun)

        # nothing installed at arms location -> install shotgun
        self.assertEqual(len(player.backpack), 0)
        arm_mod = player.active_mods[mods.ModLocation.ARMS]
        self.assertIs(arm_mod, shotgun.mod)

        # adding a second arm mod goes into the backpack
        pistol = _make_item(ObjectType.PISTOL)

        player.attempt_pickup(pistol)
        self.assertEqual(len(player.backpack), 1)
        arm_mod = player.active_mods[mods.ModLocation.ARMS]
        self.assertIs(arm_mod, shotgun.mod)
        self.assertIn(pistol.mod, player.backpack)

        # make sure we can swap the pistol with the shotgun
        player.equip(pistol.mod)
        self.assertEqual(len(player.backpack), 1)
        arm_mod = player.active_mods[mods.ModLocation.ARMS]
        self.assertEqual(arm_mod, pistol.mod)
        self.assertIn(shotgun.mod, player.backpack)


if __name__ == '__main__':
    unittest.main()

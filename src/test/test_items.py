import unittest
from typing import Tuple

from pygame.math import Vector2

import items
import model
import mods
from abilities import AbilityData
from creatures.players import Player
from data.abilities_io import load_ability_data_kwargs
from data.constructors import ItemManager
from data.items_io import load_item_data
from src.test.testing_utilities import make_player, make_item
from test.pygame_mock import initialize_pygame, initialize_gameobjects, \
    MockTimer
from tilemap import ObjectType


def setUpModule() -> None:
    initialize_pygame()
    initialize_gameobjects(ModTest.groups, ModTest.timer)


class ModTest(unittest.TestCase):
    groups = model.Groups()
    timer = MockTimer()

    def tearDown(self) -> None:
        self.groups.empty()
        self.timer.reset()

    def testmake_item_in_groups(self) -> None:
        groups = self.groups

        hp = make_item(ObjectType.HEALTHPACK)
        self.assertIn(hp, groups.all_sprites)
        self.assertIn(hp, groups.items)
        self.assertEqual(len(groups.all_sprites), 1)
        self.assertEqual(len(groups.items), 1)

        pistol = make_item(ObjectType.PISTOL)
        self.assertIn(pistol, groups.all_sprites)
        self.assertIn(pistol, groups.items)
        self.assertEqual(len(groups.all_sprites), 2)
        self.assertEqual(len(groups.items), 2)

        shotgun = make_item(ObjectType.SHOTGUN)
        self.assertIn(shotgun, groups.all_sprites)
        self.assertIn(shotgun, groups.items)
        self.assertEqual(len(groups.all_sprites), 3)
        self.assertEqual(len(groups.items), 3)

    def test_backpack_full(self) -> None:
        player = make_player()
        pistol = make_item(ObjectType.PISTOL)

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

    def test_pickup_healthpacks(self) -> None:
        player = make_player()
        hp = make_item(ObjectType.HEALTHPACK)

        backpack = player.backpack

        player.attempt_pickup(hp)
        # healthpack goes straight to active mods.
        self.assertNotIn(hp.mod, backpack)  # healthpack added to stack.
        active_mods = player.active_mods
        self.assertIn(hp.mod, active_mods.values())
        self.assertEqual(active_mods[hp.mod.loc].ability.uses_left, 1)

        hp_2 = make_item(ObjectType.HEALTHPACK)
        player.attempt_pickup(hp_2)

        self.assertNotIn(hp_2.mod, backpack)
        self.assertEqual(active_mods[hp.mod.loc].ability.uses_left, 2)

    def test_health_pack_not_used_full_health(self) -> None:
        hp, player = self._player_with_ready_healthpack()

        # health is full
        self.assertFalse(player.damaged)
        self.assertFalse(hp.mod.expended)
        use_hp_mod = player.ability_caller(hp.mod.loc)
        use_hp_mod()
        self.assertFalse(hp.mod.expended)

        # health pack doesn't work if health is full
        self.assertIn(hp.mod, player.active_mods.values())

    def test_health_pack_heals_back_to_full(self) -> None:
        hp, player = self._player_with_ready_healthpack()

        backpack = player.backpack

        # health pack fills health back up and is gone from active_mods
        player.increment_health(-5)
        self.assertTrue(player.damaged)

        # Ability is only usable after sufficient time has elapsed.
        use_hp_mod = player.ability_caller(hp.mod.loc)
        use_hp_mod()

        self.assertTrue(hp.mod.expended)
        self.assertEqual(hp.mod.ability.uses_left, 0)
        self.assertNotIn(hp.mod, backpack)
        self.assertFalse(player.damaged)
        self.assertEqual(player.health, player.max_health)

    def _player_with_ready_healthpack(self) -> Tuple[
        items.ItemObject, Player]:
        player = make_player()
        hp = make_item(ObjectType.HEALTHPACK)
        player.attempt_pickup(hp)
        while hp.mod.ability.cooldown_fraction < 1:
            self.timer.current_time += 100
        self.timer.current_time += 1
        return hp, player

    def test_add_weapons(self) -> None:
        player = make_player()
        shotgun = make_item(ObjectType.SHOTGUN)

        player.attempt_pickup(shotgun)

        # nothing installed at arms location -> install shotgun
        backpack = player.backpack
        self.assertNotIn(shotgun.mod, backpack)
        active_mods = player.active_mods
        arm_mod = active_mods[mods.ModLocation.ARMS]
        self.assertIs(arm_mod, shotgun.mod)

        # adding a second arm mod goes into the backpack
        pistol = make_item(ObjectType.PISTOL)

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

    def test_mod_stacking_in_active_mods(self) -> None:
        player = make_player()
        pos = Vector2(0, 0)
        hp = ItemManager.item(pos, ObjectType.HEALTHPACK)

        self.assertNotIn(hp.mod.loc, player.active_mods)

        player.attempt_pickup(hp)
        player_mod = player.active_mods[hp.mod.loc]
        self.assertIs(player_mod, hp.mod)
        self.assertEqual(player_mod.ability.uses_left, 1)

        player.attempt_pickup(ItemManager.item(pos, ObjectType.HEALTHPACK))
        player_mod = player.active_mods[hp.mod.loc]
        self.assertEqual(player_mod.ability.uses_left, 2)

        player.attempt_pickup(ItemManager.item(pos, ObjectType.HEALTHPACK))
        player_mod = player.active_mods[hp.mod.loc]
        self.assertEqual(player_mod.ability.uses_left, 3)

    def test_mod_stacking_in_backpack(self) -> None:
        player = make_player()
        pos = Vector2(0, 0)

        player.attempt_pickup(ItemManager.item(pos, ObjectType.PISTOL))

        self.assertFalse(player.backpack.slot_occupied(0))

        player.attempt_pickup(ItemManager.item(pos, ObjectType.ROCK))
        self.assertTrue(player.backpack.slot_occupied(0))
        self.assertEqual(player.backpack[0].ability.uses_left, 1)

        player.attempt_pickup(ItemManager.item(pos, ObjectType.ROCK))
        self.assertEqual(player.backpack[0].ability.uses_left, 2)

        player.attempt_pickup(ItemManager.item(pos, ObjectType.ROCK))
        self.assertEqual(player.backpack[0].ability.uses_left, 3)

        player.attempt_pickup(ItemManager.item(pos, ObjectType.ROCK))
        self.assertEqual(player.backpack[0].ability.uses_left, 4)

    def test_pickup_several_items(self) -> None:
        player = make_player()
        pos = Vector2(0, 0)

        laser_gun = ItemManager.item(pos, ObjectType.LASER_GUN)
        battery = ItemManager.item(pos, ObjectType.BATTERY)
        pistol = ItemManager.item(pos, ObjectType.PISTOL)
        medpack = ItemManager.item(pos, ObjectType.HEALTHPACK)

        player.attempt_pickup(laser_gun)
        self.assertIs(laser_gun.mod, player.active_mods[mods.ModLocation.ARMS])
        player.attempt_pickup(battery)
        self.assertIs(battery.mod, player.active_mods[mods.ModLocation.CHEST])
        player.attempt_pickup(pistol)
        self.assertIn(pistol.mod, player.backpack)
        self.assertTrue(player.backpack.slot_occupied(0))
        player.attempt_pickup(medpack)
        self.assertIn(medpack.mod, player.backpack)
        self.assertTrue(player.backpack.slot_occupied(1))

    def test_creation_of_usable_items_from_data(self) -> None:
        player = make_player()
        item_data = load_item_data('pistol')
        pistol_ability = AbilityData(**load_ability_data_kwargs('pistol'))

        pistol = items.ItemFromData(item_data, Vector2(0, 0))
        player.attempt_pickup(pistol)

        self.assertIs(pistol.mod, player.active_mods[pistol.mod.loc])

        use_pistol = player.ability_caller(mods.ModLocation.ARMS)
        self.timer.current_time += pistol_ability.cool_down_time + 1

        use_pistol()
        self.assertEqual(len(self.groups.bullets), 1)


if __name__ == '__main__':
    unittest.main()

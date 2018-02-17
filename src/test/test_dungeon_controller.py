import unittest

from unittest.mock import Mock

from pygame.math import Vector2

import mods
from creatures.humanoids import HumanoidData, Status, Inventory
from src.test.pygame_mock import initialize_pygame
from src.test.testing_utilities import make_dungeon_controller, make_player
from data.constructors import build_map_object
from view import DungeonView


def setUpModule() -> None:
    initialize_pygame()


class DungeonControllerTest(unittest.TestCase):
    def test_health_pack_in_backpack_does_not_prevent_equip(self) -> None:
        dng_ctrl = make_dungeon_controller()
        fake_player_data = HumanoidData(Status(100), Inventory())
        dng_ctrl.set_player_data(fake_player_data)
        inventory = fake_player_data.inventory

        pos = Vector2(0, 0)
        pistol = build_map_object('pistol', pos)
        shotgun = build_map_object('shotgun', pos)

        inventory.attempt_pickup(pistol)
        inventory.attempt_pickup(
            shotgun)  # shotgun mod goes to slot 0 in backpack
        inventory.attempt_pickup(
            build_map_object('healthpack', pos))
        inventory.attempt_pickup(
            build_map_object('healthpack', pos))

        mock_view = Mock(spec=DungeonView)

        mock_view.selected_item = lambda: 0
        dng_ctrl._view = mock_view

        pistol_mod = pistol.mod
        shotgun_mod = shotgun.mod
        weapon_loc = pistol_mod.loc
        self.assertEqual(inventory.active_mods[weapon_loc], pistol_mod)
        dng_ctrl._equip_mod_in_backpack()
        self.assertEqual(inventory.active_mods[weapon_loc], shotgun_mod)

    def test_items_do_not_move_in_backpack_after_equip(self) -> None:
        player = make_player()

        pos = Vector2(0, 0)
        shotgun = build_map_object('shotgun', pos)

        inventory = player.inventory
        inventory.attempt_pickup(build_map_object('pistol', pos))
        inventory.attempt_pickup(
            shotgun)  # shotgun mod goes to slot 0 in backpack

        inventory.attempt_pickup(build_map_object('healthpack', pos))
        shotgun_2 = build_map_object('shotgun', pos)
        inventory.attempt_pickup(shotgun_2)

        self.assertIs(inventory.backpack[1], shotgun_2.mod)
        inventory.equip(shotgun.mod)
        self.assertIs(inventory.backpack[1], shotgun_2.mod)

    def test_equip_nothing_from_backpack(self) -> None:
        dungeon = make_dungeon_controller()

        # ensure this method doesn't fail (nothing selected)
        dungeon._equip_mod_in_backpack()

    def test_set_player_data(self) -> None:
        ctrl = make_dungeon_controller()
        player = make_player()
        pos = Vector2(0, 0)
        pistol = build_map_object('pistol', pos)
        shotgun = build_map_object('shotgun', pos)

        player.inventory.attempt_pickup(pistol)
        player.inventory.attempt_pickup(
            shotgun)  # shotgun mod goes to slot 0 in backpack
        player.status.increment_health(-10)

        ctrl.set_player_data(player.data)

        self.assertEqual(ctrl._dungeon.player.data, player.data)

    def test_unequip(self) -> None:
        dng_ctrl = make_dungeon_controller()

        fake_player_data = HumanoidData(Status(100), Inventory())
        dng_ctrl.set_player_data(fake_player_data)
        inventory = fake_player_data.inventory

        pos = Vector2(0, 0)
        pistol = build_map_object('pistol', pos)

        inventory.attempt_pickup(pistol)

        # ensure nothing in backpack
        self.assertEqual(inventory.backpack._slots_filled, 0)

        # ensure one mod equiped
        arm_mod = inventory.active_mods[mods.ModLocation.ARMS]
        self.assertTrue(arm_mod is not None)

        # unequip
        inventory.unequip(mods.ModLocation.ARMS)

        # ensure something now in backpack
        self.assertEqual(inventory.backpack._slots_filled, 1)

        # ensure nothing on the arms
        self.assertNotIn(mods.ModLocation.ARMS, inventory.active_mods)


if __name__ == '__main__':
    unittest.main()

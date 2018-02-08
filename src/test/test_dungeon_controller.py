import unittest
from typing import Any
from unittest.mock import Mock

from pygame.math import Vector2

import mods
from src.test.pygame_mock import initialize_pygame
from src.test.testing_utilities import make_dungeon_controller, make_player
from tilemap import ObjectType
from data.constructors import build_map_object
from view import DungeonView


def setUpModule() -> None:
    initialize_pygame()


class DungeonControllerTest(unittest.TestCase):
    def test_health_pack_in_backpack_does_not_prevent_equip(self) -> None:
        dng_ctrl = make_dungeon_controller()
        player = dng_ctrl.player

        pos = Vector2(0, 0)
        pistol = build_map_object(ObjectType.PISTOL, pos)
        shotgun = build_map_object(ObjectType.SHOTGUN, pos)

        player.inventory.attempt_pickup(pistol)
        player.inventory.attempt_pickup(
            shotgun)  # shotgun mod goes to slot 0 in backpack
        player.inventory.attempt_pickup(
            build_map_object(ObjectType.HEALTHPACK, pos))
        player.inventory.attempt_pickup(
            build_map_object(ObjectType.HEALTHPACK, pos))

        mock_view = Mock(spec=DungeonView)

        mock_view.selected_item = lambda: 0
        dng_ctrl._view = mock_view

        pistol_mod = pistol.mod
        shotgun_mod = shotgun.mod
        weapon_loc = pistol_mod.loc
        self.assertEqual(player.inventory.active_mods[weapon_loc], pistol_mod)
        dng_ctrl._equip_mod_in_backpack()
        self.assertEqual(player.inventory.active_mods[weapon_loc], shotgun_mod)

    def test_items_do_not_move_in_backpack_after_equip(self) -> None:
        player = make_player()

        pos = Vector2(0, 0)
        shotgun = build_map_object(ObjectType.SHOTGUN, pos)

        inventory = player.inventory
        inventory.attempt_pickup(build_map_object(ObjectType.PISTOL, pos))
        inventory.attempt_pickup(
            shotgun)  # shotgun mod goes to slot 0 in backpack

        inventory.attempt_pickup(build_map_object(ObjectType.HEALTHPACK, pos))
        shotgun_2 = build_map_object(ObjectType.SHOTGUN, pos)
        inventory.attempt_pickup(shotgun_2)

        self.assertIs(inventory.backpack[1], shotgun_2.mod)
        inventory.equip(shotgun.mod)
        self.assertIs(inventory.backpack[1], shotgun_2.mod)

    def test_game_over(self) -> None:
        ctrl = make_dungeon_controller()
        player = ctrl.player
        ctrl.player.status.increment_health(- 2 * player.status.max_health)

        self.assertTrue(ctrl.game_over())

    def test_should_exit(self) -> None:
        ctrl = make_dungeon_controller()
        # ctrl isn't over when we start
        self.assertFalse(ctrl.should_exit())

        for conflict_name in ctrl._dungeon.conflicts.conflicts:
            ctrl._dungeon.conflicts.conflicts[conflict_name].group.empty()

        # can't exit until teleport
        self.assertFalse(ctrl.should_exit())

        # assume the player asks to teleport
        ctrl._teleported = True

        # ensure the ctrl is now over
        self.assertTrue(ctrl.should_exit())

    def test_equip_nothing_from_backpack(self) -> None:
        dungeon = make_dungeon_controller()

        # ensure this method doesn't fail (nothing selected)
        dungeon._equip_mod_in_backpack()

    def test_pass_mouse_pos(self) -> None:
        import dungeon_controller

        def origin() -> Any:
            return (0, 0)

        def far_awway() -> Any:
            return (1000, 2000)

        for func in [origin, far_awway]:
            dungeon_controller.pg.mouse.get_pos = func

            dungeon = make_dungeon_controller()
            dungeon._pass_mouse_pos_to_player()

            self.assertEqual(dungeon.player._mouse_pos, func())

    def test_set_player(self) -> None:
        dungeon = make_dungeon_controller()
        player = make_player()
        pos = Vector2(0, 0)
        pistol = build_map_object(ObjectType.PISTOL, pos)
        shotgun = build_map_object(ObjectType.SHOTGUN, pos)

        player.inventory.attempt_pickup(pistol)
        player.inventory.attempt_pickup(
            shotgun)  # shotgun mod goes to slot 0 in backpack
        player.status.increment_health(-10)

        dungeon.set_player(player)

        # make sure the player in the dungeon has 10 less health and the pistol
        # equiped and the shotgun in the backpack
        set_player = dungeon.player
        self.assertEqual(set_player.status.health,
                         player.status.max_health - 10)
        self.assertEqual(set_player.inventory.backpack._slots_filled, 1)
        self.assertEqual(len(set_player.inventory.active_mods.values()), 1)

    def test_unequip(self) -> None:
        dng_ctrl = make_dungeon_controller()
        player = dng_ctrl.player

        pos = Vector2(0, 0)
        pistol = build_map_object(ObjectType.PISTOL, pos)
        player.inventory.attempt_pickup(pistol)

        # ensure nothing in backpack
        self.assertEqual(player.inventory.backpack._slots_filled, 0)

        # ensure one mod equiped
        arm_mod = player.inventory.active_mods[mods.ModLocation.ARMS]
        self.assertTrue(arm_mod is not None)

        # unequip
        player.inventory.unequip(mods.ModLocation.ARMS)

        # ensure something now in backpack
        self.assertEqual(player.inventory.backpack._slots_filled, 1)

        # ensure nothing on the arms
        self.assertNotIn(mods.ModLocation.ARMS, player.inventory.active_mods)


if __name__ == '__main__':
    unittest.main()

import unittest
from typing import Any
from unittest.mock import Mock

from pygame.math import Vector2

import mods
from items.item_manager import ItemManager
from src.test.pygame_mock import initialize_pygame
from src.test.testing_utilities import make_dungeon_controller, make_player
from tilemap import ObjectType
from view import DungeonView


def setUpModule() -> None:
    initialize_pygame()


def tearDownModule() -> None:
    from model import GameObject, DynamicObject
    GameObject.gameobjects_initialized = False
    DynamicObject.dynamic_initialized = False
    from creatures.mobs import Mob
    Mob.class_initialized = False
    from abilities import Ability
    Ability.class_initialized = False


class DungeonControllerTest(unittest.TestCase):
    def test_health_pack_in_backpack_does_not_prevent_equip(self) -> None:
        dng_ctrl = make_dungeon_controller()
        player = dng_ctrl.player

        pos = Vector2(0, 0)
        pistol = ItemManager.item(pos, ObjectType.PISTOL)
        shotgun = ItemManager.item(pos, ObjectType.SHOTGUN)

        player.attempt_pickup(pistol)
        player.attempt_pickup(shotgun)  # shotgun mod goes to slot 0 in backpack
        player.attempt_pickup(ItemManager.item(pos, ObjectType.HEALTHPACK))
        player.attempt_pickup(ItemManager.item(pos, ObjectType.HEALTHPACK))

        mock_view = Mock(spec=DungeonView)

        mock_view.selected_item = lambda: 0
        dng_ctrl._view = mock_view

        pistol_mod = pistol.mod
        shotgun_mod = shotgun.mod
        weapon_loc = pistol_mod.loc
        self.assertEqual(player.active_mods[weapon_loc], pistol_mod)
        dng_ctrl.equip_mod_in_backpack()
        self.assertEqual(player.active_mods[weapon_loc], shotgun_mod)

    def test_items_do_not_move_in_backpack_after_equip(self) -> None:
        player = make_player()

        pos = Vector2(0, 0)
        shotgun = ItemManager.item(pos, ObjectType.SHOTGUN)

        player.attempt_pickup(ItemManager.item(pos, ObjectType.PISTOL))
        player.attempt_pickup(shotgun)  # shotgun mod goes to slot 0 in backpack

        player.attempt_pickup(ItemManager.item(pos, ObjectType.HEALTHPACK))
        shotgun_2 = ItemManager.item(pos, ObjectType.SHOTGUN)
        player.attempt_pickup(shotgun_2)

        self.assertIs(player.backpack[1], shotgun_2.mod)
        player.equip(shotgun.mod)
        self.assertIs(player.backpack[1], shotgun_2.mod)

    def test_game_over(self) -> None:
        dungeon = make_dungeon_controller()
        player = dungeon.player
        dungeon.player.increment_health(- 2 * player.max_health)

        self.assertTrue(dungeon.game_over())

    def test_should_exit(self) -> None:
        dungeon = make_dungeon_controller()
        # dungeon isn't over when we start
        self.assertFalse(dungeon.should_exit())

        for conflict_name in dungeon._conflicts.conflicts:
            dungeon._conflicts.conflicts[conflict_name].group.empty()

        # can't exit until teleport
        self.assertFalse(dungeon.should_exit())

        # assume the player asks to teleport
        dungeon.teleported = True

        # ensure the dungeon is now over
        self.assertTrue(dungeon.should_exit())


    def test_equip_nothing_from_backpack(self) -> None:
        dungeon = make_dungeon_controller()

        # ensure this method doesn't fail (nothing selected)
        dungeon.equip_mod_in_backpack()

    def test_pass_mouse_pos(self) -> None:
        import dungeon_controller

        def origin() -> Any:
            return (0, 0)

        def far_awway() -> Any:
            return (1000, 2000)

        for func in [origin, far_awway]:
            dungeon_controller.pg.mouse.get_pos = func

            dungeon = make_dungeon_controller()
            dungeon.pass_mouse_pos_to_player()

            self.assertEqual(dungeon.player._mouse_pos, func())

    def test_handle_hud_not_clicked(self) -> None:
        import controller
        def not_clicked() -> Any:
            return controller.NOT_CLICKED

        dungeon = make_dungeon_controller()
        dungeon.get_clicked_pos = not_clicked

        self.assertFalse(dungeon.try_handle_hud())

    def test_handle_hud_clicked_elsewhere(self) -> None:
        def clicked() -> Any:
            return (-1000, -4000)

        dungeon = make_dungeon_controller()
        dungeon.get_clicked_pos = clicked

        self.assertFalse(dungeon.try_handle_hud())

    def test_set_player(self) -> None:
        dungeon = make_dungeon_controller()
        player = make_player()
        pos = Vector2(0, 0)
        pistol = ItemManager.item(pos, ObjectType.PISTOL)
        shotgun = ItemManager.item(pos, ObjectType.SHOTGUN)

        player.attempt_pickup(pistol)
        player.attempt_pickup(shotgun)  # shotgun mod goes to slot 0 in backpack
        player.increment_health(-10)

        dungeon.set_player(player)

        # make sure the player in the dungeon has 10 less health and the pistol
        # equiped and the shotgun in the backpack
        set_player = dungeon.player
        self.assertEqual(set_player.health, player.max_health - 10)
        self.assertEqual(set_player.backpack._slots_filled, 1)
        self.assertEqual(len(set_player.active_mods.values()), 1)

    def test_unequip(self) -> None:
        dng_ctrl = make_dungeon_controller()
        player = dng_ctrl.player

        pos = Vector2(0, 0)
        pistol = ItemManager.item(pos, ObjectType.PISTOL)
        player.attempt_pickup(pistol)

        # ensure nothing in backpack
        self.assertEqual(player.backpack._slots_filled, 0)

        # ensure one mod equiped
        arm_mod = player.active_mods[mods.ModLocation.ARMS]
        self.assertTrue(arm_mod is not None)

        # unequip
        player.unequip(mods.ModLocation.ARMS)

        # ensure something now in backpack
        self.assertEqual(player.backpack._slots_filled, 1)

        # ensure nothing on the arms
        self.assertNotIn(mods.ModLocation.ARMS, player.active_mods)


if __name__ == '__main__':
    unittest.main()

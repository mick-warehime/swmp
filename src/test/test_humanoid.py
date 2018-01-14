import unittest
from typing import Tuple
from pygame.math import Vector2
from pygame.sprite import Group, LayeredUpdates
import model
from items.rocks import RockObject
from src.test.pygame_mock import MockTimer, initialize_pygame, \
    initialize_gameobjects
from itertools import product
import math
from src.test.testing_utilities import make_player, make_mob
from test import dummy_audio_video


def setUpModule() -> None:
    initialize_pygame()
    initialize_gameobjects(HumanoidsTest.groups, HumanoidsTest.timer)
    dummy_audio_video


def _dist(pos_0: Vector2, pos_1: Vector2) -> float:
    dist_squared = (pos_0.x - pos_1.x) ** 2 + (pos_0.y - pos_1.y) ** 2
    return math.sqrt(dist_squared)


class HumanoidsTest(unittest.TestCase):
    groups = model.Groups()
    timer = MockTimer()

    def tearDown(self) -> None:
        self.groups.empty()
        self.timer.reset()

    def test_groups_immutable_container(self) -> None:
        groups = model.Groups()

        self.assertIsInstance(groups.walls, Group)
        self.assertIsInstance(groups.all_sprites, LayeredUpdates)

        with self.assertRaises(AttributeError):
            groups.walls = Group()

    def test_humanoid_increment_health(self) -> None:
        player = make_player()
        max_health = player.health

        player.increment_health(-1)
        self.assertEqual(player.health, max_health - 1)
        player.increment_health(100)
        self.assertEqual(player.health, max_health)
        player.increment_health(-max_health - 2)
        self.assertEqual(player.health, 0)

    def test_player_move(self) -> None:
        player = make_player()

        original_pos = Vector2(0, 0)
        self.assertEqual(player.pos, original_pos)

        player.translate_down()
        player.translate_left()
        player.update()
        player.translate_down()
        player.translate_left()
        player.update()

        speed = 56
        expected = Vector2(-speed, speed)
        self.assertEqual(player.pos, expected)

        # velocity set to zero after each update
        player.update()
        self.assertEqual(player.pos, expected)

        # up movement is twice as fast as other moves, so we only do it once.
        player.translate_up()
        player.translate_right()
        player.update()
        player.translate_right()
        player.translate_up()
        player.update()
        self.assertEqual(player.pos, original_pos)

    def test_player_turn(self) -> None:
        player = make_player()

        # start player at origin facing right
        player.pos = (0, 0)
        player.rot = 0

        # +x is to the right of player - no rotation
        player.set_mouse_pos((100, 0))
        player.turn()
        self.assertAlmostEqual(player.rot, 0, 1)

        # -y is above player - faces top of screen
        player.set_mouse_pos((0, -100))
        player.turn()
        self.assertAlmostEqual(player.rot, 90, 1)

        # +y is above below - faces bottom of screen
        player.set_mouse_pos((0, 100))
        player.turn()
        self.assertAlmostEqual(player.rot, 270, 1)

        # -x is left of player
        player.set_mouse_pos((-100, 0))
        player.turn()
        self.assertAlmostEqual(player.rot, 180, 1)

    def test_player_move_to_mouse(self) -> None:

        def normalize(pos: Tuple[float, float]) \
                -> Tuple[float, float]:
            x, y = pos
            length = math.sqrt(x ** 2 + y ** 2)
            if length == 0:
                return (0.0, 0.0)
            return (x / length, y / length)

        player = make_player()

        # test that the player moves in the same direction as mouse
        possible_positions = [[0, 100, -100]] * 2
        for x, y in product(*possible_positions):
            player.pos = (0, 0)
            player.rot = 0
            player.set_mouse_pos((x, y))
            player.move_towards_mouse()
            player.update()

            # player direction
            p_hat = normalize(player.pos)

            # mouse direction
            m_hat = normalize((x, y))

            self.assertAlmostEqual(p_hat[0], m_hat[0], 8)
            self.assertAlmostEqual(p_hat[1], m_hat[1], 8)

    def test_mouse_too_close(self) -> None:
        # stop moving when you get close to the mouse
        player = make_player()

        player.pos = (0, 0)
        player.rot = 0
        player.set_mouse_pos((1, 1))
        player.move_towards_mouse()
        player.update()

        self.assertEqual(player.pos[0], 0)
        self.assertEqual(player.pos[1], 0)

    def test_player_stop(self) -> None:
        player = make_player()

        original_pos = Vector2(0, 0)
        self.assertEqual(player.pos, original_pos)

        player.translate_down()
        player.translate_left()
        player.stop_x()
        player.update()
        expected = Vector2(0, 28)
        self.assertEqual(player.pos, expected)

        player.translate_down()
        player.translate_left()
        player.stop_y()
        player.update()
        expected = Vector2(-28, 28)
        self.assertEqual(player.pos, expected)

    def test_mob_move_to_player(self) -> None:
        player = make_player()
        mob = make_mob(player)

        initial_dist = _dist(player.pos, mob.pos)
        mob.update()
        final_dist = _dist(player.pos, mob.pos)

        self.assertLess(final_dist, initial_dist)

    def test_mob_damage_and_death(self) -> None:
        groups = self.groups
        mob = make_mob()
        mob.increment_health(61 - mob._max_health)
        mob.increment_health(31 - 61)
        mob.increment_health(0 - 31)

        self.assertIn(mob, groups.mobs)

        mob.update()
        self.assertNotIn(mob, groups.mobs)

    def test_pickup_rock_adds_to_active_mods(self) -> None:
        player = make_player()

        player.attempt_pickup(RockObject(player.pos))

        self.assertFalse(player.backpack.slot_occupied(0))

        player.attempt_pickup(RockObject(player.pos))
        self.assertFalse(player.backpack.slot_occupied(0))


if __name__ == '__main__':
    unittest.main()

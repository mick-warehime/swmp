import unittest
from typing import Union, Tuple, Callable
import os
from pygame.math import Vector2
import pygame
from pygame.sprite import Group, LayeredUpdates
import model
import humanoid as hmn
from mods import ShotgunMod
from src.test.pygame_mock import MockTimer, Pygame, initialize_pygame
from tilemap import ObjectType
from weapon import Weapon, Bullet, MuzzleFlash
from itertools import product
import math

# This allows for running tests without actually generating a screen display
# or audio output.
os.environ['SDL_VIDEODRIVER'] = 'dummy'
os.environ['SDL_AUDIODRIVER'] = 'dummy'

pg = Pygame()


def _make_pistol() -> Weapon:
    return Weapon(ObjectType.PISTOL, ModelTest.timer, ModelTest.groups)


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
    return hmn.Mob(pos, player)


def setUpModule() -> None:
    initialize_pygame()

    # Normally I would be running unit tests, but it is not possible to check
    #  exceptions once the classes are initialized.
    _assert_runtime_exception_raised(_make_player)
    model.GameObject.initialize_gameobjects(ModelTest.groups)

    _assert_runtime_exception_raised(_make_player)
    model.DynamicObject.initialize_dynamic_objects(ModelTest.timer)

    _assert_runtime_exception_raised(_make_player)
    hmn.Player.init_class()

    _assert_runtime_exception_raised(_make_mob)
    blank_screen = pygame.Surface((800, 600))
    hmn.Mob.init_class(blank_screen)

    player = _make_player()
    player.set_weapon(ObjectType.PISTOL)
    ModelTest.timer._time += player._weapon.shoot_rate + 1
    _assert_runtime_exception_raised(player.shoot)
    Bullet.initialize_class()

    # I would call this in test_mod.py, but it looks like the coverage
    # command somehow initializes ShotgunMod too early there.
    _assert_runtime_exception_raised(ShotgunMod)

    ModelTest.groups.empty()
    ModelTest.timer.reset()


def _assert_runtime_exception_raised(tested_fun: Callable) -> None:
    exception_raised = False
    try:
        tested_fun()
    except RuntimeError:
        exception_raised = True
    assert exception_raised


def _dist(pos_0: Vector2, pos_1: Vector2) -> float:
    dist_squared = (pos_0.x - pos_1.x) ** 2 + (pos_0.y - pos_1.y) ** 2
    return math.sqrt(dist_squared)


class ModelTest(unittest.TestCase):
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

    def test_weapon_shoot_instantiates_bullet_and_flash(self) -> None:
        groups = self.groups
        weapon = _make_pistol()
        pos = pygame.math.Vector2(0, 0)
        rot = 0.0

        self.assertEqual(len(groups.all_sprites), 0)
        weapon.shoot(pos, rot)
        # Check if a MuzzleFlash and Bullet sprite were created
        sprites = groups.all_sprites
        num_bullets = 0
        num_flashes = 0
        num_others = 0
        for sp in sprites:
            if isinstance(sp, Bullet):
                num_bullets += 1
            elif isinstance(sp, MuzzleFlash):
                num_flashes += 1
            else:
                num_others += 1

        self.assertEqual(num_bullets, 1)
        self.assertEqual(num_flashes, 1)
        self.assertEqual(num_others, 0)

    def test_weapon_cannot_shoot_after_firing(self) -> None:
        timer = self.timer
        weapon = _make_pistol()
        pos = pygame.math.Vector2(0, 0)
        rot = 0.0

        # Weapon is instantiated at the current time, so at first it cannot
        # shoot. We must wait until timer.current_time> weapon.shoot_rate -
        # weapon._last_shot
        self.assertFalse(weapon.can_shoot)
        timer._time += weapon.shoot_rate
        self.assertFalse(weapon.can_shoot)
        timer._time += 1
        self.assertTrue(weapon.can_shoot)
        weapon.shoot(pos, rot)
        self.assertFalse(weapon.can_shoot)

    def test_player_shoot_no_shot(self) -> None:
        groups = self.groups
        timer = self.timer
        player = _make_player()
        player.set_weapon(ObjectType.PISTOL)

        self.assertEqual(len(groups.bullets), 0)
        player.shoot()
        self.assertEqual(len(groups.bullets), 0)
        timer._time += player._weapon.shoot_rate + 1
        player.shoot()
        self.assertEqual(len(groups.bullets), 1)

    def test_player_shoot_kickback(self) -> None:
        timer = self.timer
        player = _make_player()
        player.set_weapon(ObjectType.PISTOL)

        old_vel = (player._vel.x, player._vel.y)

        timer._time += player._weapon.shoot_rate + 1
        player.shoot()

        new_vel = (player._vel.x, player._vel.y)
        expected_vel = (-player._weapon.kick_back + old_vel[0], old_vel[1])
        self.assertEqual(new_vel, expected_vel)

    def test_player_set_weapon(self) -> None:
        player = _make_player()
        player.set_weapon(ObjectType.PISTOL)
        self.assertEqual(player._weapon._item_type, ObjectType.PISTOL)
        player.set_weapon(ObjectType.SHOTGUN)
        self.assertEqual(player._weapon._item_type, ObjectType.SHOTGUN)

    def test_player_shoot_no_weapon(self) -> None:
        groups = self.groups
        player = _make_player()

        # No weapon equipped so no bullets come out.
        self.assertEqual(len(groups.bullets), 0)
        player.shoot()
        self.assertEqual(len(groups.bullets), 0)

    def test_humanoid_increment_health(self) -> None:
        player = _make_player()
        max_health = player.health

        player.increment_health(-1)
        self.assertEqual(player.health, max_health - 1)
        player.increment_health(100)
        self.assertEqual(player.health, max_health)
        player.increment_health(-max_health - 2)
        self.assertEqual(player.health, 0)

    def test_player_move(self) -> None:
        player = _make_player()

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
        player = _make_player()

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

        player = _make_player()

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
        player = _make_player()

        player.pos = (0, 0)
        player.rot = 0
        player.set_mouse_pos((1, 1))
        player.move_towards_mouse()
        player.update()

        self.assertEqual(player.pos[0], 0)
        self.assertEqual(player.pos[1], 0)

    def test_player_stop(self) -> None:
        player = _make_player()

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
        player = _make_player()
        mob = _make_mob(player)

        initial_dist = _dist(player.pos, mob.pos)
        mob.update()
        final_dist = _dist(player.pos, mob.pos)

        self.assertLess(final_dist, initial_dist)

    def test_mob_damage_and_death(self) -> None:
        groups = self.groups
        mob = _make_mob()
        mob.draw_health()

        mob.increment_health(61 - mob._max_health)
        mob.draw_health()
        mob.increment_health(31 - 61)
        mob.draw_health()
        mob.increment_health(0 - 31)
        mob.draw_health()

        self.assertIn(mob, groups.mobs)

        mob.update()
        self.assertNotIn(mob, groups.mobs)


if __name__ == '__main__':
    unittest.main()

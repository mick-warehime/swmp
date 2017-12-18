import unittest
from typing import Union
import sys, os

from pygame.math import Vector2

sys.path.append('../../')
sys.path.append('../')
sys.path.append('.')
import pygame
from pygame.sprite import Group, LayeredUpdates
import model
import humanoid as hmn
import images
import sounds
from src.test.pygame_mock import MockTimer, Pygame
from weapon import Weapon, Bullet, MuzzleFlash

# This allows for running tests without actually generating a screen display
# or audio output.
os.environ['SDL_VIDEODRIVER'] = 'dummy'
os.environ['SDL_AUDIODRIVER'] = 'dummy'

pg = Pygame()


class Connection(object):
    groups = model.Groups()
    timer = MockTimer()


def _make_pistol(timer: Union[None, MockTimer] = None,
                 groups: Union[None, model.Groups] = None) -> Weapon:
    if groups is None:
        groups = model.Groups()
    if timer is None:
        timer = MockTimer()
    return Weapon('pistol', timer, groups)


def _make_player(groups: Union[None, model.Groups] = None) -> hmn.Player:
    if groups is None:
        groups = model.Groups()
    pos = pygame.math.Vector2(0, 0)
    return hmn.Player(groups, pos)


def _make_mob(player: hmn.Player,
              groups: Union[None, model.Groups] = None,
              pos: Union[Vector2, None] = None) -> hmn.Mob:
    if groups is None:
        groups = model.Groups()
    if pos is None:
        pos = pygame.math.Vector2(0, 0)

    return hmn.Mob(groups, pos, player)


def setUpModule() -> None:
    pygame.display.set_mode((600, 400))
    pygame.mixer.pre_init(44100, -16, 4, 2048)
    pygame.init()
    images.initialize_images()
    sounds.initialize_sounds()

    try:
        _make_player()
        raise AssertionError('Expected a RuntimeError to be raised because '
                             'Player is not initialized.')
    except RuntimeError:
        hmn.Player.init_class()

    try:
        _make_player()
        raise AssertionError('Expected a RuntimeError to be raised because '
                             'Humanoid is not initialized.')
    except RuntimeError:
        hmn.Humanoid.init_class(Connection.groups.walls, Connection.timer)

    player = _make_player()

    try:
        _make_mob(player)
        raise AssertionError('Expected a RuntimeError to be raised because '
                             'Mob is not initialized.')
    except RuntimeError:
        blank_screen = pygame.Surface((800, 600))
        hmn.Mob.init_class(blank_screen, Connection.groups)

    player.kill()


class ModelTest(unittest.TestCase):
    def tearDown(self):
        groups = Connection.groups
        groups.walls.empty
        groups.mobs.empty
        groups.bullets.empty
        groups.all_sprites.empty
        groups.items.empty

        Connection.timer.reset()

    def test_groups_immutable_container(self) -> None:
        groups = model.Groups()

        self.assertIsInstance(groups.walls, Group)
        self.assertIsInstance(groups.all_sprites, LayeredUpdates)

        with self.assertRaises(AttributeError):
            groups.walls = Group()

    def test_weapon_wrong_label_raises_exception(self) -> None:
        with self.assertRaisesRegex(ValueError, 'not defined in settings.py.'):
            groups = model.Groups()
            timer = MockTimer()
            Weapon('bad', timer, groups)

    def test_weapon_shoot_instantiates_bullet_and_flash(self) -> None:
        groups = model.Groups()
        weapon = _make_pistol(groups=groups)
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
        timer = MockTimer()
        weapon = _make_pistol(timer)
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

    def test_weapon_set(self) -> None:
        weapon = _make_pistol()

        self.assertLess(weapon.bullet_count, 2)
        weapon.set('shotgun')
        self.assertGreater(weapon.bullet_count, 1)

    def test_player_shoot_no_shot(self) -> None:
        groups = model.Groups()
        timer = Connection.timer
        player = _make_player(groups=groups)

        self.assertEqual(len(groups.bullets), 0)
        player.shoot()
        self.assertEqual(len(groups.bullets), 0)
        timer._time += player._weapon.shoot_rate + 1
        player.shoot()
        self.assertEqual(len(groups.bullets), 1)

    def test_player_shoot_kickback(self) -> None:
        timer = Connection.timer
        player = _make_player()

        old_vel = (player._vel.x, player._vel.y)

        timer._time += player._weapon.shoot_rate + 1
        player.shoot()

        new_vel = (player._vel.x, player._vel.y)
        expected_vel = (-player._weapon.kick_back + old_vel[0], old_vel[1])
        self.assertEqual(new_vel, expected_vel)

    def test_player_set_weapon(self) -> None:
        player = _make_player()
        self.assertEqual(player._weapon._label, 'pistol')
        player.set_weapon('shotgun')
        self.assertEqual(player._weapon._label, 'shotgun')

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

        player.move_down()
        player.move_left()
        player.update()
        player.move_down()
        player.move_left()
        player.update()
        expected = Vector2(-28, -28)
        self.assertEqual(player.pos, expected)

        # velocity set to zero after each update
        player.update()
        self.assertEqual(player.pos, expected)

        # up movement is twice as fast as other moves, so we only do it once.
        player.move_up()
        player.move_right()
        player.update()
        player.move_right()
        player.update()
        self.assertEqual(player.pos, original_pos)

    def test_player_rot(self) -> None:
        player = _make_player()

        self.assertEqual(player.rot, 0)

        player.turn_clockwise()
        player.update()
        expected = 320
        self.assertEqual(player.rot, expected)

        player.update()
        self.assertEqual(player.rot, expected)

        player.turn_counterclockwise()
        player.update()
        self.assertEqual(player.rot, 0)

    def test_player_stop(self) -> None:
        player = _make_player()

        original_pos = Vector2(0, 0)
        self.assertEqual(player.pos, original_pos)

        player.move_down()
        player.move_left()
        player.stop_x()
        player.update()
        expected = Vector2(0, -14)
        self.assertEqual(player.pos, expected)

        player.move_down()
        player.move_left()
        player.stop_y()
        player.update()
        expected = Vector2(-14, -14)
        self.assertEqual(player.pos, expected)


if __name__ == '__main__':
    unittest.main()

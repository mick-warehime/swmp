import unittest
from typing import Union

import pygame
from pygame.sprite import Group, LayeredUpdates

import model, images, sounds
from test.pygame_mock import MockTimer
from . import pygame_mock

# This allows for running tests without actually generating a screen display.
import os
# os.putenv('SDL_VIDEODRIVER', 'fbcon')
os.environ['SDL_VIDEODRIVER'] = 'dummy'
# os.putenv('SDL_AUDIODRIVER', 'dummy')
os.environ['SDL_AUDIODRIVER'] = 'dummy'


pg = pygame_mock.Pygame()


def setUpModule() -> None:
    pygame.display.set_mode((600, 400))
    pygame.mixer.pre_init(44100, -16, 4, 2048)
    pygame.init()
    images.initialize_images()
    sounds.initialize_sounds()


def _make_pistol(timer: Union[None, MockTimer] = None,
                 groups: Union[None, model.Groups] = None) -> model.Weapon:
    if groups is None:
        groups = model.Groups()
    if timer is None:
        timer = MockTimer()
    weapon = model.Weapon('pistol', timer, groups)
    return weapon


def _make_player(timer: Union[None, MockTimer] = None,
                 groups: Union[None, model.Groups] = None) -> model.Player:
    if groups is None:
        groups = model.Groups()
    if timer is None:
        timer = MockTimer()
    pos = pygame.math.Vector2(0, 0)
    player = model.Player(groups, timer, pos)
    return player


class ModelTest(unittest.TestCase):
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
            model.Weapon('bad', timer, groups)

    def test_weapon_shoot_instantiates_bullet_and_flash(self) -> None:
        groups = model.Groups()
        weapon = _make_pistol(groups=groups)
        pos = pygame.math.Vector2(0, 0)
        rot = 0.0

        self.assertEqual(len(groups.all_sprites), 0)
        weapon.shoot(pos, rot)
        # Check if a MuzzleFlash and Bullet sprite were created
        self.assertEqual(len(groups.all_sprites), 2)
        self.assertEqual(len(groups.bullets), 1)

    def test_weapon_cannot_shoot_after_firing(self) -> None:
        timer = MockTimer()
        weapon = _make_pistol(timer)
        pos = pygame.math.Vector2(0, 0)
        rot = 0.0

        # Weapon is instantiated at the current time, so at first it cannot
        # shoot. We must wait until timer.current_time> weapon.shoot_rate -
        # weapon._last_shot
        self.assertFalse(weapon.can_shoot)
        timer.time += weapon.shoot_rate
        self.assertFalse(weapon.can_shoot)
        timer.time += 1
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
        timer = MockTimer()
        player = _make_player(timer=timer, groups=groups)

        self.assertEqual(len(groups.bullets), 0)
        player.shoot()
        self.assertEqual(len(groups.bullets), 0)
        timer.time += player._weapon.shoot_rate + 1
        player.shoot()
        self.assertEqual(len(groups.bullets), 1)

    def test_player_shoot_kickback(self) -> None:
        timer = MockTimer()
        player = _make_player(timer=timer)

        old_vel = (player._vel.x, player._vel.y)

        timer.time += player._weapon.shoot_rate + 1
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


if __name__ == '__main__':
    unittest.main()

import unittest

import pygame
from pygame.sprite import Group, LayeredUpdates

import model, images, sounds
from test.pygame_mock import MockTimer
from . import pygame_mock

pg = pygame_mock.Pygame()


def setUpModule() -> None:
    pygame.display.set_mode((600, 400))
    pygame.mixer.pre_init(44100, -16, 4, 2048)
    pygame.init()
    images.initialize_images()
    sounds.initialize_sounds()


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
        timer = MockTimer()
        weapon = model.Weapon('pistol', timer, groups)
        pos = pygame.math.Vector2(0, 0)
        rot = 0.0

        self.assertEqual(len(groups.all_sprites), 0)
        weapon.shoot(pos, rot)
        # Check if a MuzzleFlash and Bullet sprite were created
        self.assertEqual(len(groups.all_sprites), 2)
        self.assertEqual(len(groups.bullets), 1)

    def test_weapon_cannot_shoot_after_firing(self) -> None:
        groups = model.Groups()
        timer = MockTimer()
        weapon = model.Weapon('pistol', timer, groups)
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
        groups = model.Groups()
        timer = MockTimer()
        weapon = model.Weapon('pistol', timer, groups)

        self.assertLess(weapon.bullet_count, 2)
        weapon.set('shotgun')
        self.assertGreater(weapon.bullet_count, 1)


if __name__ == '__main__':
    unittest.main()

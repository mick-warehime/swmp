import unittest
from pygame.math import Vector2

import model
from abilities import GenericAbility, AbilityData
from data.abilities_io import load_ability_data_kwargs
from src.test.pygame_mock import MockTimer, initialize_pygame, \
    initialize_gameobjects
from src.test.testing_utilities import make_player

import src.test.dummy_audio_video


def setUpModule() -> None:
    initialize_pygame()
    initialize_gameobjects(WeaponsTest.groups, WeaponsTest.timer)


class WeaponsTest(unittest.TestCase):
    groups = model.Groups()
    timer = MockTimer()

    def tearDown(self) -> None:
        self.groups.empty()
        self.timer.reset()

    def test_fire_projectile_distance_independent_of_count(self) -> None:
        player = make_player()
        num_updates = 100

        data_dict = load_ability_data_kwargs('shotgun')
        data_dict['projectile_count'] = 1
        ability_data = AbilityData(**data_dict)

        fire_little_bullet = GenericAbility(ability_data)

        fire_little_bullet.use(player)

        self.assertEqual(len(self.groups.bullets), 1)
        bullet = self.groups.bullets.sprites()[0]
        first_pos = Vector2(bullet.pos.x, bullet.pos.y)

        for _ in range(num_updates):
            self.groups.bullets.update()

        one_disp = (bullet.pos - first_pos).length()

        many = 10
        ability_data = ability_data._replace(projectile_count=many)
        fire_little_bullet = GenericAbility(ability_data)

        self.groups.bullets.empty()
        fire_little_bullet.use(player)
        self.assertEqual(len(self.groups.bullets), many)

        bullet = self.groups.bullets.sprites()[0]
        first_pos = Vector2(bullet.pos.x, bullet.pos.y)

        for _ in range(num_updates):
            self.groups.bullets.update()

        many_disp = (bullet.pos - first_pos).length()

        self.assertLess(0.5 * many_disp, one_disp)

    # def test_projectile_data_eq(self) -> None:
    #     bullet_data = ProjectileData(**load_projectile_data_kwargs('bullet'))
    #     other_data = ProjectileData(**load_projectile_data_kwargs('bullet'))
    #
    #     self.assertEqual(bullet_data, other_data)
    #     self.assertIsNot(bullet_data, other_data)

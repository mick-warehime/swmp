import unittest
from pygame.math import Vector2

import model
from abilities import ProjectileAbilityData, FireProjectile
from images import LITTLE_BULLET
from projectiles import ProjectileData
from src.test.pygame_mock import MockTimer, initialize_pygame, \
    initialize_gameobjects
from src.test.testing_utilities import make_player


def setUpModule() -> None:
    initialize_pygame()
    initialize_gameobjects(WeaponsTest.groups, WeaponsTest.timer)


class WeaponsTest(unittest.TestCase):
    groups = model.Groups()
    timer = MockTimer()
    bullet_data = ProjectileData(hits_player=False, damage=25,
                                 speed=500,
                                 max_lifetime=500,
                                 image_file=LITTLE_BULLET)

    def tearDown(self) -> None:
        self.groups.empty()
        self.timer.reset()

    def test_fire_projectile_distance_independent_of_count(self) -> None:
        player = make_player()
        num_updates = 100

        ability_data = ProjectileAbilityData(900,
                                             projectile_data=self.bullet_data,
                                             projectile_count=1,
                                             kickback=300, spread=20)

        fire_little_bullet = FireProjectile(ability_data)

        fire_little_bullet.use(player)

        self.assertEqual(len(self.groups.bullets), 1)
        bullet = self.groups.bullets.sprites()[0]
        first_pos = Vector2(bullet.pos.x, bullet.pos.y)

        for _ in range(num_updates):
            self.groups.bullets.update()

        one_disp = (bullet.pos - first_pos).length()

        many = 10
        ability_data.projectile_count = many
        fire_little_bullet = FireProjectile(ability_data)

        self.groups.bullets.empty()
        fire_little_bullet.use(player)
        self.assertEqual(len(self.groups.bullets), many)

        bullet = self.groups.bullets.sprites()[0]
        first_pos = Vector2(bullet.pos.x, bullet.pos.y)

        for _ in range(num_updates):
            self.groups.bullets.update()

        many_disp = (bullet.pos - first_pos).length()

        self.assertLess(0.5 * many_disp, one_disp)

import unittest

from pygame.math import Vector2

import model
from data.input_output import load_projectile_data_kwargs
from projectiles import ProjectileData, SimpleProjectile, ProjectileFactory, \
    FancyProjectile
from test.pygame_mock import initialize_pygame,  MockTimer
from view import images


def setUpModule() -> None:
    initialize_pygame()
    model.initialize(ProjectilesTest.groups, ProjectilesTest.timer)


class ProjectilesTest(unittest.TestCase):
    groups = model.Groups()
    timer = MockTimer()

    def tearDown(self) -> None:
        self.groups.empty()
        self.timer.reset()

    def test_projectile_moves_in_direction(self) -> None:
        direction = Vector2(1, 0)
        speed = 100
        basic_data = ProjectileData(True, 10, speed, 100, images.LITTLE_BULLET)

        bullet = SimpleProjectile(Vector2(0, 0), direction, basic_data)

        steps = 100
        for _ in range(steps):
            bullet.update()
        time_elapsed = self.timer.dt * steps

        dx = bullet.pos.x
        dy = bullet.pos.y

        expected_dx = time_elapsed * speed * direction.x
        self.assertLess(abs(expected_dx - dx), time_elapsed * speed / 10)

        expected_dy = time_elapsed * speed * direction.y
        self.assertLess(abs(expected_dy - dy), time_elapsed * speed / 10)

    def test_projectile_dies_after_lifetime_exceeded(self) -> None:
        direction = Vector2(1, 0)
        basic_data = ProjectileData(False, 10, 100, 100, images.LITTLE_BULLET)

        bullet = SimpleProjectile(Vector2(0, 0), direction, basic_data)

        self.assertIn(bullet, self.groups.bullets)

        self.timer.current_time += bullet.max_lifetime + 1

        bullet.update()
        self.assertNotIn(bullet, self.groups.bullets)

    def test_projectile_with_drops_on_kill_instantiates_object(self) -> None:
        lifetime = 10
        dropper_data = ProjectileData(False, 10, 10, lifetime,
                                      images.LITTLE_BULLET,
                                      drops_on_kill='rock')
        rock_dropper = FancyProjectile(Vector2(0, 0), Vector2(1, 0),
                                       dropper_data)

        self.assertEqual(len(self.groups.items), 0)
        self.timer.current_time += lifetime + 1
        rock_dropper.update()
        self.assertEqual(len(self.groups.items), 1)

    def test_fancy_projectile_rotating_image_changes_width(self) -> None:

        data = ProjectileData(False, 10, 10, 20, 'laser_blue.png',
                              rotating_image=True)
        projectile = FancyProjectile(Vector2(0, 0), Vector2(1, 0), data)

        initial_width = projectile.image.get_width()
        self.timer.current_time += 10
        projectile.update()

        final_width = projectile.image.get_width()
        self.assertNotEqual(initial_width, final_width)

    def test_fancy_projectile_angled_image_changes_angle(self) -> None:

        data = ProjectileData(**load_projectile_data_kwargs('laser'))
        assert data.angled_image
        projectile_y = FancyProjectile(Vector2(0, 0), Vector2(0, 1), data)
        projectile_x = FancyProjectile(Vector2(0, 0), Vector2(1, 0), data)

        image_y = projectile_y.image
        image_x = projectile_x.image

        self.assertEqual(image_y.get_width(), image_x.get_height())
        self.assertEqual(image_y.get_height(), image_x.get_width())

    def test_projectile_factory_build(self) -> None:
        basic_data = ProjectileData(True, 10, 100, 100, images.LITTLE_BULLET)
        factory = ProjectileFactory(basic_data)

        self.assertEqual(len(self.groups.all_sprites), 0)

        for k in range(5):
            factory.build(Vector2(0, 0), Vector2(1, 0))
            self.assertEqual(len(self.groups.all_sprites), k + 1)
            self.assertEqual(len(self.groups.enemy_projectiles), k + 1)
            self.assertEqual(len(self.groups.bullets), 0)

    def test_projectile_data_eq(self) -> None:
        rock_data_0 = ProjectileData(**load_projectile_data_kwargs('rock'))
        rock_data_1 = ProjectileData(**load_projectile_data_kwargs('rock'))
        self.assertEqual(rock_data_0, rock_data_1)

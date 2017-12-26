import unittest
import os

from pygame.math import Vector2

import model
import humanoids as hmn
from abilities import FireShotgun
from src.test.pygame_mock import MockTimer, Pygame, initialize_pygame, \
    initialize_gameobjects

# This allows for running tests without actually generating a screen display
# or audio output.
os.environ['SDL_VIDEODRIVER'] = 'dummy'
os.environ['SDL_AUDIODRIVER'] = 'dummy'

pg = Pygame()


def setUpModule() -> None:
    initialize_pygame()
    initialize_gameobjects(WeaponsTest.groups, WeaponsTest.timer)


def _make_player() -> hmn.Player:
    pos = Vector2(0, 0)
    player = hmn.Player(pos)
    return player


class WeaponsTest(unittest.TestCase):
    groups = model.Groups()
    timer = MockTimer()

    def tearDown(self) -> None:
        self.groups.empty()
        self.timer.reset()

    def test_fire_projectile_distance_independent_of_count(self) -> None:
        player = _make_player()
        num_updates = 100

        FireShotgun._projectile_count = 1
        fire_little_bullet = FireShotgun()

        fire_little_bullet.use(player)

        self.assertEqual(len(self.groups.bullets), 1)
        bullet = self.groups.bullets.sprites()[0]
        first_pos = Vector2(bullet.pos.x, bullet.pos.y)

        for _ in range(num_updates):
            self.groups.bullets.update()

        one_disp = (bullet.pos - first_pos).length()

        many = 10
        FireShotgun._projectile_count = many
        self.groups.bullets.empty()
        fire_little_bullet.use(player)
        self.assertEqual(len(self.groups.bullets), many)

        bullet = self.groups.bullets.sprites()[0]
        first_pos = Vector2(bullet.pos.x, bullet.pos.y)

        for _ in range(num_updates):
            self.groups.bullets.update()

        many_disp = (bullet.pos - first_pos).length()

        self.assertLess(0.5 * many_disp, one_disp)

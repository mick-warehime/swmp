import unittest
import os
import pygame
import model
import humanoids as hmn
from abilities import FirePistol, FireShotgun, Heal
from src.test.pygame_mock import MockTimer, Pygame, initialize_pygame, \
    initialize_gameobjects
from weapons import Bullet, MuzzleFlash

# This allows for running tests without actually generating a screen display
# or audio output.
os.environ['SDL_VIDEODRIVER'] = 'dummy'
os.environ['SDL_AUDIODRIVER'] = 'dummy'

pg = Pygame()


def setUpModule() -> None:
    initialize_pygame()
    initialize_gameobjects(ModTest.groups, ModTest.timer)


def _make_player() -> hmn.Player:
    pos = pygame.math.Vector2(0, 0)
    player = hmn.Player(pos)
    return player


class ModTest(unittest.TestCase):
    groups = model.Groups()
    timer = MockTimer()

    def tearDown(self) -> None:
        self.groups.empty()
        self.timer.reset()

    def test_fire_projectile_cannot_shoot_at_first(self):
        fire_pistol = FirePistol()

        self.assertFalse(fire_pistol.can_use)
        self.timer.current_time += FirePistol._cool_down
        self.assertFalse(fire_pistol.can_use)
        self.timer.current_time += 1
        self.assertTrue(fire_pistol.can_use)

    def test_fireprojectile_use_instantiates_bullet_and_flash(self) -> None:
        groups = self.groups
        player = _make_player()
        fire_pistol = FirePistol()

        self.assertEqual(len(groups.all_sprites), 1)
        fire_pistol.use(player)
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
        self.assertEqual(num_others, 1)

    def test_fireprojectile_use_ignores_can_use(self):
        player = _make_player()
        fire_pistol = FirePistol()

        self.assertEqual(len(self.groups.bullets), 0)
        self.assertFalse(fire_pistol.can_use)
        fire_pistol.use(player)
        self.assertEqual(len(self.groups.bullets), 1)

    def test_fireprojectile_cannot_use_after_firing(self) -> None:
        player = _make_player()
        fire_pistol = FirePistol()
        self.timer.current_time += FirePistol._cool_down + 1

        self.assertTrue(fire_pistol.can_use)
        fire_pistol.use(player)
        self.assertFalse(fire_pistol.can_use)

    def test_player_shoot_kickback(self) -> None:
        player = _make_player()
        fire_pistol = FirePistol()

        old_vel = (player._vel.x, player._vel.y)
        fire_pistol.use(player)
        new_vel = (player._vel.x, player._vel.y)

        expected_vel = (-fire_pistol._kickback + old_vel[0], old_vel[1])
        self.assertEqual(new_vel, expected_vel)

    def test_fire_shotgun_many_bullets(self) -> None:
        player = _make_player()
        fire_shotty = FireShotgun()

        self.assertEqual(len(self.groups.bullets), 0)
        fire_shotty.use(player)
        self.assertEqual(len(self.groups.bullets),
                         FireShotgun._projectile_count)

    def test_heal_player_not_damaged(self) -> None:
        player = _make_player()
        heal_amount = 10
        heal = Heal(3, heal_amount)

        max_health = player.max_health
        self.assertEqual(player.health, max_health)
        heal.use(player)
        self.assertEqual(player.health, max_health)
        self.assertEqual(heal.uses_left, 3)

    def test_heal_player_damaged_to_full(self) -> None:
        player = _make_player()
        heal_amount = 10
        heal = Heal(3, heal_amount)

        max_health = player.max_health
        player.increment_health(-heal_amount + 2)
        heal.use(player)
        self.assertEqual(player.health, max_health)
        self.assertEqual(heal.uses_left, 2)

    def test_heal_player_damaged_correct_amount(self) -> None:
        player = _make_player()
        heal_amount = 10
        heal = Heal(3, heal_amount)

        max_health = player.max_health
        player.increment_health(-heal_amount - 2)
        heal.use(player)
        self.assertEqual(player.health, max_health - 2)
        self.assertEqual(heal.uses_left, 2)

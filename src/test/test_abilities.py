import unittest
import model
from abilities import FirePistol, FireShotgun, Heal
from src.test.pygame_mock import MockTimer, initialize_pygame, \
    initialize_gameobjects
from weapons import Projectile, MuzzleFlash
from src.test.testing_utilities import make_player


def setUpModule() -> None:
    initialize_pygame()
    initialize_gameobjects(AbilitiesTest.groups, AbilitiesTest.timer)


class AbilitiesTest(unittest.TestCase):
    groups = model.Groups()
    timer = MockTimer()

    def tearDown(self) -> None:
        self.groups.empty()
        self.timer.reset()

    def test_fire_projectile_cannot_shoot_at_first(self) -> None:
        fire_pistol = FirePistol()

        self.assertFalse(fire_pistol.can_use)
        self.timer.current_time += FirePistol._cool_down_time
        self.assertFalse(fire_pistol.can_use)
        self.timer.current_time += 1
        self.assertTrue(fire_pistol.can_use)

    def test_fireprojectile_use_instantiates_bullet_and_flash(self) -> None:
        groups = self.groups
        player = make_player()
        fire_pistol = FirePistol()

        self.assertEqual(len(groups.all_sprites), 1)
        fire_pistol.use(player)
        # Check if a MuzzleFlash and Projectile sprite were created
        sprites = groups.all_sprites
        num_bullets = 0
        num_flashes = 0
        num_others = 0
        for sp in sprites:
            if isinstance(sp, Projectile):
                num_bullets += 1
            elif isinstance(sp, MuzzleFlash):
                num_flashes += 1
            else:
                num_others += 1

        self.assertEqual(num_bullets, 1)
        self.assertEqual(num_flashes, 1)
        self.assertEqual(num_others, 1)

    def test_fireprojectile_use_ignores_can_use(self) -> None:
        player = make_player()
        fire_pistol = FirePistol()

        self.assertEqual(len(self.groups.bullets), 0)
        self.assertFalse(fire_pistol.can_use)
        fire_pistol.use(player)
        self.assertEqual(len(self.groups.bullets), 1)

    def test_fireprojectile_cannot_use_after_firing(self) -> None:
        player = make_player()
        fire_pistol = FirePistol()
        self.timer.current_time += FirePistol._cool_down_time + 1

        self.assertTrue(fire_pistol.can_use)
        fire_pistol.use(player)
        self.assertFalse(fire_pistol.can_use)

    def test_player_shoot_kickback(self) -> None:
        player = make_player()
        fire_pistol = FirePistol()

        old_vel = (player._vel.x, player._vel.y)
        fire_pistol.use(player)
        new_vel = (player._vel.x, player._vel.y)

        expected_vel = (-fire_pistol._kickback + old_vel[0], old_vel[1])
        self.assertEqual(new_vel, expected_vel)

    def test_fire_shotgun_many_bullets(self) -> None:
        player = make_player()
        fire_shotty = FireShotgun()

        self.assertEqual(len(self.groups.bullets), 0)
        fire_shotty.use(player)
        self.assertEqual(len(self.groups.bullets),
                         FireShotgun._projectile_count)

    def test_heal_player_not_damaged(self) -> None:
        player = make_player()
        heal_amount = 10
        heal = Heal(3, heal_amount)

        max_health = player.max_health
        self.assertEqual(player.health, max_health)
        heal.use(player)
        self.assertEqual(player.health, max_health)
        self.assertEqual(heal.uses_left, 3)

    def test_heal_player_damaged_to_full(self) -> None:
        player = make_player()
        heal_amount = 10
        heal = Heal(3, heal_amount)

        max_health = player.max_health
        player.increment_health(-heal_amount + 2)
        heal.use(player)
        self.assertEqual(player.health, max_health)
        self.assertEqual(heal.uses_left, 2)

    def test_heal_player_damaged_correct_amount(self) -> None:
        player = make_player()
        heal_amount = 10
        heal = Heal(3, heal_amount)

        max_health = player.max_health
        player.increment_health(-heal_amount - 2)
        heal.use(player)
        self.assertEqual(player.health, max_health - 2)
        self.assertEqual(heal.uses_left, 2)

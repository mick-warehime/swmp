import unittest
from copy import copy

import model
from abilities import ProjectileAbilityData, FireProjectile, \
    RegenerationAbilityData, RegenerationAbility, AbilityData
from data.abilities_io import load_ability_data
from images import BULLET_IMG
from src.test.pygame_mock import MockTimer, initialize_pygame, \
    initialize_gameobjects
from projectiles import Projectile, ProjectileData
from items.bullet_weapons import MuzzleFlash, pistol_fire_sound
from src.test.testing_utilities import make_player


def setUpModule() -> None:
    initialize_pygame()
    initialize_gameobjects(AbilitiesTest.groups, AbilitiesTest.timer)

    ability_data = load_ability_data('pistol')
    ability_data.fire_effects = [MuzzleFlash]

    AbilitiesTest.projectile_ability_data = ability_data


class AbilitiesTest(unittest.TestCase):
    groups = model.Groups()
    timer = MockTimer()
    projectile_ability_data = None

    def tearDown(self) -> None:
        self.groups.empty()
        self.timer.reset()

    def test_fire_projectile_cannot_shoot_at_first(self) -> None:
        fire_pistol = FireProjectile(self.projectile_ability_data)

        self.assertFalse(fire_pistol.can_use)
        self.timer.current_time += fire_pistol._cool_down_time
        self.assertFalse(fire_pistol.can_use)
        self.timer.current_time += 1
        self.assertTrue(fire_pistol.can_use)

    def test_fireprojectile_use_instantiates_bullet_and_flash(self) -> None:
        groups = self.groups
        player = make_player()
        fire_pistol = FireProjectile(self.projectile_ability_data)

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
        fire_pistol = FireProjectile(self.projectile_ability_data)

        self.assertEqual(len(self.groups.bullets), 0)
        self.assertFalse(fire_pistol.can_use)
        fire_pistol.use(player)
        self.assertEqual(len(self.groups.bullets), 1)

    def test_fireprojectile_cannot_use_after_firing(self) -> None:
        player = make_player()
        fire_pistol = FireProjectile(self.projectile_ability_data)
        self.timer.current_time += fire_pistol._cool_down_time + 1

        self.assertTrue(fire_pistol.can_use)
        fire_pistol.use(player)
        self.assertFalse(fire_pistol.can_use)

    def test_player_shoot_kickback(self) -> None:
        player = make_player()
        fire_pistol = FireProjectile(self.projectile_ability_data)

        old_vel = (player._vel.x, player._vel.y)
        fire_pistol.use(player)
        new_vel = (player._vel.x, player._vel.y)

        expected_vel = (-fire_pistol._kickback + old_vel[0], old_vel[1])
        self.assertEqual(new_vel, expected_vel)

    def test_fire_many_bullets(self) -> None:
        player = make_player()
        ability_data = copy(self.projectile_ability_data)  # type: ignore
        projectile_count = 15
        ability_data.projectile_count = projectile_count
        fire_many = FireProjectile(ability_data)

        self.assertEqual(len(self.groups.bullets), 0)
        fire_many.use(player)
        self.assertEqual(len(self.groups.bullets),
                         projectile_count)

    def test_heal_player_not_damaged(self) -> None:
        player = make_player()
        heal_amount = 10
        data = RegenerationAbilityData(cool_down_time=300, finite_uses=True,
                                       uses_left=3, heal_amount=heal_amount)
        heal = RegenerationAbility(data)

        max_health = player.max_health
        self.assertEqual(player.health, max_health)
        heal.use(player)
        self.assertEqual(player.health, max_health)
        self.assertEqual(heal.uses_left, 3)

    def test_heal_player_damaged_to_full(self) -> None:
        player = make_player()
        heal_amount = 10
        data = RegenerationAbilityData(cool_down_time=300, finite_uses=True,
                                       uses_left=3, heal_amount=heal_amount)
        heal = RegenerationAbility(data)

        max_health = player.max_health
        player.increment_health(-heal_amount + 2)
        heal.use(player)
        self.assertEqual(player.health, max_health)
        self.assertEqual(heal.uses_left, 2)

    def test_heal_player_damaged_correct_amount(self) -> None:
        player = make_player()
        heal_amount = 10
        data = RegenerationAbilityData(cool_down_time=300, finite_uses=True,
                                       uses_left=3, heal_amount=heal_amount)
        heal = RegenerationAbility(data)

        max_health = player.max_health
        player.increment_health(-heal_amount - 2)
        heal.use(player)
        self.assertEqual(player.health, max_health - 2)
        self.assertEqual(heal.uses_left, 2)

    def test_regenerate_player_energy_correct_amount(self) -> None:
        player = make_player()
        recharge_amount = 15
        data = RegenerationAbilityData(cool_down_time=300, finite_uses=True,
                                       uses_left=2,
                                       recharge_amount=recharge_amount)
        recharge = RegenerationAbility(data)

        source = player.energy_source
        starting_energy = source.max_energy
        energy_expended = 20

        source.expend_energy(energy_expended)
        self.assertEqual(source.energy_available,
                         starting_energy - energy_expended)

        recharge.use(player)
        self.assertEqual(source.energy_available,
                         starting_energy - energy_expended + recharge_amount)
        self.assertEqual(recharge.uses_left, 1)

        recharge.use(player)
        self.assertEqual(source.energy_available, starting_energy)
        self.assertEqual(recharge.uses_left, 0)

    def test_ability_data_equality(self) -> None:

        base_data = AbilityData(cool_down_time=300, finite_uses=True,
                                uses_left=3)
        base_data_2 = AbilityData(cool_down_time=300, finite_uses=True,
                                  uses_left=3)
        self.assertEqual(base_data, base_data_2)

        base_data = AbilityData(cool_down_time=300, finite_uses=True,
                                uses_left=3)
        base_data_2 = AbilityData(cool_down_time=300, finite_uses=True,
                                  uses_left=2)
        self.assertEqual(base_data, base_data_2)

        base_data = AbilityData(cool_down_time=301, finite_uses=True,
                                uses_left=3)
        base_data_2 = AbilityData(cool_down_time=300, finite_uses=True,
                                  uses_left=3)
        self.assertNotEqual(base_data, base_data_2)

        self.assertNotEqual(base_data, 1)
        self.assertNotEqual(1, base_data)

        reg_data = RegenerationAbilityData(300, heal_amount=10,
                                           finite_uses=True, uses_left=1)
        reg_data_2 = RegenerationAbilityData(300, heal_amount=10,
                                             finite_uses=True, uses_left=1)
        self.assertEqual(reg_data, reg_data_2)

        reg_data = RegenerationAbilityData(301, heal_amount=10,
                                           finite_uses=True, uses_left=1)
        reg_data_2 = RegenerationAbilityData(300, heal_amount=10,
                                             finite_uses=True, uses_left=1)
        self.assertNotEqual(reg_data, reg_data_2)

        reg_data = RegenerationAbilityData(300, heal_amount=10,
                                           finite_uses=True, uses_left=1)
        reg_data_2 = RegenerationAbilityData(300, heal_amount=11,
                                             finite_uses=True, uses_left=1)
        self.assertNotEqual(reg_data, reg_data_2)

        reg_data = RegenerationAbilityData(300, heal_amount=10,
                                           finite_uses=True, uses_left=1)
        reg_data_2 = RegenerationAbilityData(300, heal_amount=10,
                                             finite_uses=True, uses_left=2)
        self.assertEqual(reg_data, reg_data_2)

        reg_data = RegenerationAbilityData(300, heal_amount=10,
                                           recharge_amount=1,
                                           finite_uses=True, uses_left=1)
        reg_data_2 = RegenerationAbilityData(300, heal_amount=10,
                                             finite_uses=True, uses_left=1)
        self.assertNotEqual(reg_data, reg_data_2)

        proj_data = ProjectileData(hits_player=False, damage=75,
                                   speed=1000,
                                   max_lifetime=400,
                                   image_file=BULLET_IMG)
        proj_ability_data_0 = ProjectileAbilityData(
            250, projectile_data=proj_data, projectile_count=1,
            kickback=200, spread=5,
            fire_effects=[pistol_fire_sound, MuzzleFlash])

        proj_ability_data_1 = ProjectileAbilityData(
            250, projectile_data=proj_data, projectile_count=1,
            kickback=200, spread=5,
            fire_effects=[pistol_fire_sound, MuzzleFlash])

        self.assertEqual(proj_ability_data_0, proj_ability_data_1)

        proj_data = ProjectileData(hits_player=False, damage=75,
                                   speed=1000,
                                   max_lifetime=400,
                                   image_file=BULLET_IMG)
        proj_ability_data_0 = ProjectileAbilityData(
            251, projectile_data=proj_data, projectile_count=1,
            kickback=200, spread=5,
            fire_effects=[pistol_fire_sound, MuzzleFlash])

        proj_ability_data_1 = ProjectileAbilityData(
            250, projectile_data=proj_data, projectile_count=1,
            kickback=200, spread=5,
            fire_effects=[pistol_fire_sound, MuzzleFlash])

        self.assertNotEqual(proj_ability_data_0, proj_ability_data_1)

        proj_data = ProjectileData(hits_player=False, damage=75,
                                   speed=1000,
                                   max_lifetime=400,
                                   image_file=BULLET_IMG)
        proj_ability_data_0 = ProjectileAbilityData(
            250, projectile_data=proj_data, projectile_count=2,
            kickback=200, spread=5,
            fire_effects=[pistol_fire_sound, MuzzleFlash])

        proj_ability_data_1 = ProjectileAbilityData(
            250, projectile_data=proj_data, projectile_count=1,
            kickback=200, spread=5,
            fire_effects=[pistol_fire_sound, MuzzleFlash])

        self.assertNotEqual(proj_ability_data_0, proj_ability_data_1)

        proj_data = ProjectileData(hits_player=False, damage=75,
                                   speed=1000,
                                   max_lifetime=400,
                                   image_file=BULLET_IMG)
        proj_ability_data_0 = ProjectileAbilityData(
            250, projectile_data=proj_data, projectile_count=1,
            kickback=201, spread=5,
            fire_effects=[pistol_fire_sound, MuzzleFlash])

        proj_ability_data_1 = ProjectileAbilityData(
            250, projectile_data=proj_data, projectile_count=1,
            kickback=200, spread=5,
            fire_effects=[pistol_fire_sound, MuzzleFlash])

        self.assertNotEqual(proj_ability_data_0, proj_ability_data_1)

        proj_data = ProjectileData(hits_player=False, damage=75,
                                   speed=1000,
                                   max_lifetime=400,
                                   image_file=BULLET_IMG)
        proj_ability_data_0 = ProjectileAbilityData(
            250, projectile_data=proj_data, projectile_count=1,
            kickback=200, spread=5,
            fire_effects=[pistol_fire_sound, MuzzleFlash])

        proj_ability_data_1 = ProjectileAbilityData(
            250, projectile_data=proj_data, projectile_count=1,
            kickback=200, spread=6,
            fire_effects=[pistol_fire_sound, MuzzleFlash])

        self.assertNotEqual(proj_ability_data_0, proj_ability_data_1)

        proj_data = ProjectileData(hits_player=False, damage=75,
                                   speed=1000,
                                   max_lifetime=400,
                                   image_file=BULLET_IMG)
        proj_ability_data_0 = ProjectileAbilityData(
            250, projectile_data=proj_data, projectile_count=1,
            kickback=200, spread=5,
            fire_effects=[pistol_fire_sound, MuzzleFlash])

        proj_ability_data_1 = ProjectileAbilityData(
            250, projectile_data=proj_data, projectile_count=1,
            kickback=200, spread=5,
            fire_effects=[pistol_fire_sound])

        self.assertNotEqual(proj_ability_data_0, proj_ability_data_1)

        proj_data_0 = ProjectileData(hits_player=False, damage=75,
                                     speed=1000,
                                     max_lifetime=400,
                                     image_file=BULLET_IMG)
        proj_data_1 = ProjectileData(hits_player=False, damage=75,
                                     speed=1001,
                                     max_lifetime=400,
                                     image_file=BULLET_IMG)
        proj_ability_data_0 = ProjectileAbilityData(
            250, projectile_data=proj_data_0, projectile_count=1,
            kickback=200, spread=5,
            fire_effects=[pistol_fire_sound, MuzzleFlash])

        proj_ability_data_1 = ProjectileAbilityData(
            250, projectile_data=proj_data_1, projectile_count=1,
            kickback=200, spread=5,
            fire_effects=[pistol_fire_sound, MuzzleFlash])

        self.assertNotEqual(proj_ability_data_0, proj_ability_data_1)

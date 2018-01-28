import unittest

import model
from abilities import GenericAbility, AbilityData
from data.input_output import load_ability_data_kwargs
from src.test.pygame_mock import MockTimer, initialize_pygame, \
    initialize_gameobjects
from projectiles import Projectile, MuzzleFlash
from src.test.testing_utilities import make_player


def setUpModule() -> None:
    initialize_pygame()
    initialize_gameobjects(AbilitiesTest.groups, AbilitiesTest.timer)

    ability_data = AbilityData(**load_ability_data_kwargs('pistol'))

    AbilitiesTest.projectile_ability_data = ability_data


class AbilitiesTest(unittest.TestCase):
    groups = model.Groups()
    timer = MockTimer()
    projectile_ability_data: AbilityData = None

    def tearDown(self) -> None:
        self.groups.empty()
        self.timer.reset()

    def test_fire_projectile_cannot_shoot_at_first(self) -> None:
        fire_pistol = GenericAbility(self.projectile_ability_data)

        self.assertFalse(fire_pistol.can_use('dummy_arg'))
        self.timer.current_time += self.projectile_ability_data.cool_down_time
        self.assertFalse(fire_pistol.can_use('dummy_arg'))
        self.timer.current_time += 1
        self.assertTrue(fire_pistol.can_use('dummy_arg'))

    def test_fireprojectile_use_instantiates_bullet_and_flash(self) -> None:
        groups = self.groups
        player = make_player()
        fire_pistol = GenericAbility(self.projectile_ability_data)

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
        fire_pistol = GenericAbility(self.projectile_ability_data)

        self.assertEqual(len(self.groups.bullets), 0)
        self.assertFalse(fire_pistol.can_use('dummy_arg'))
        fire_pistol.use(player)
        self.assertEqual(len(self.groups.bullets), 1)

    def test_fireprojectile_cannot_use_after_firing(self) -> None:
        player = make_player()
        fire_pistol = GenericAbility(self.projectile_ability_data)
        self.timer.current_time += \
            self.projectile_ability_data.cool_down_time + 1

        self.assertTrue(fire_pistol.can_use('dummy_arg'))
        fire_pistol.use(player)
        self.assertFalse(fire_pistol.can_use('dummy_arg'))

    def test_player_shoot_kickback(self) -> None:
        player = make_player()
        fire_pistol = GenericAbility(self.projectile_ability_data)

        old_vel = (player.motion.vel.x, player.motion.vel.y)
        fire_pistol.use(player)
        new_vel = (player.motion.vel.x, player.motion.vel.y)

        kickback = self.projectile_ability_data.kickback
        expected_vel = (-kickback + old_vel[0], old_vel[1])
        self.assertEqual(new_vel, expected_vel)

    def test_fire_many_bullets(self) -> None:
        player = make_player()

        projectile_count = 15
        ability_data = self.projectile_ability_data._replace(
            projectile_count=projectile_count)
        fire_many = GenericAbility(ability_data)

        self.assertEqual(len(self.groups.bullets), 0)
        fire_many.use(player)
        self.assertEqual(len(self.groups.bullets),
                         projectile_count)

    def test_heal_player_not_damaged(self) -> None:
        player = make_player()
        heal_amount = 10
        data = AbilityData(cool_down_time=300, finite_uses=True,
                           uses_left=3, heal_amount=heal_amount)
        heal = GenericAbility(data)

        max_health = player.status.max_health
        self.assertEqual(player.status.health, max_health)
        self.assertFalse(heal.can_use(player))

        # use implements a heal anyway
        heal.use(player)
        self.assertEqual(player.status.health, max_health)
        self.assertEqual(heal.uses_left, 2)

    def test_heal_player_damaged_to_full(self) -> None:
        player = make_player()
        heal_amount = 10
        data = AbilityData(cool_down_time=300, finite_uses=True,
                           uses_left=3, heal_amount=heal_amount)
        heal = GenericAbility(data)

        max_health = player.status.max_health
        player.status.increment_health(-heal_amount + 2)
        heal.use(player)
        self.assertEqual(player.status.health, max_health)
        self.assertEqual(heal.uses_left, 2)

    def test_heal_player_damaged_correct_amount(self) -> None:
        player = make_player()
        heal_amount = 10
        data = AbilityData(cool_down_time=300, finite_uses=True,
                           uses_left=3, heal_amount=heal_amount)
        heal = GenericAbility(data)

        max_health = player.status.max_health
        player.status.increment_health(-heal_amount - 2)
        heal.use(player)
        self.assertEqual(player.status.health, max_health - 2)
        self.assertEqual(heal.uses_left, 2)

    def test_regenerate_player_energy_correct_amount(self) -> None:
        player = make_player()
        recharge_amount = 15
        data = AbilityData(cool_down_time=300, finite_uses=True,
                           uses_left=2,
                           recharge_amount=recharge_amount)
        recharge = GenericAbility(data)

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

        reg_data = AbilityData(300, heal_amount=10,
                               finite_uses=True, uses_left=1)
        reg_data_2 = AbilityData(300, heal_amount=10,
                                 finite_uses=True, uses_left=1)
        self.assertEqual(reg_data, reg_data_2)

        reg_data = AbilityData(301, heal_amount=10,
                               finite_uses=True, uses_left=1)
        reg_data_2 = AbilityData(300, heal_amount=10,
                                 finite_uses=True, uses_left=1)
        self.assertNotEqual(reg_data, reg_data_2)

        reg_data = AbilityData(300, heal_amount=10,
                               finite_uses=True, uses_left=1)
        reg_data_2 = AbilityData(300, heal_amount=11,
                                 finite_uses=True, uses_left=1)
        self.assertNotEqual(reg_data, reg_data_2)

        reg_data = AbilityData(300, heal_amount=10,
                               finite_uses=True, uses_left=1)
        reg_data_2 = AbilityData(300, heal_amount=10,
                                 finite_uses=True, uses_left=2)
        self.assertEqual(reg_data, reg_data_2)

        reg_data = AbilityData(300, heal_amount=10,
                               recharge_amount=1,
                               finite_uses=True, uses_left=1)
        reg_data_2 = AbilityData(300, heal_amount=10,
                                 finite_uses=True, uses_left=1)
        self.assertNotEqual(reg_data, reg_data_2)

        proj_ability_data_0 = AbilityData(
            250, projectile_label='bullet', projectile_count=1,
            kickback=200, spread=5)

        proj_ability_data_1 = AbilityData(
            250, projectile_label='bullet', projectile_count=1,
            kickback=200, spread=5)

        self.assertEqual(proj_ability_data_0, proj_ability_data_1)

        proj_ability_data_0 = AbilityData(
            251, projectile_label='bullet', projectile_count=1,
            kickback=200, spread=5)

        proj_ability_data_1 = AbilityData(
            250, projectile_label='bullet', projectile_count=1,
            kickback=200, spread=5)

        self.assertNotEqual(proj_ability_data_0, proj_ability_data_1)

        proj_ability_data_0 = AbilityData(
            250, projectile_label='bullet', projectile_count=2,
            kickback=200, spread=5)

        proj_ability_data_1 = AbilityData(
            250, projectile_label='bullet', projectile_count=1,
            kickback=200, spread=5)

        self.assertNotEqual(proj_ability_data_0, proj_ability_data_1)

        proj_ability_data_0 = AbilityData(
            250, projectile_label='bullet', projectile_count=1,
            kickback=201, spread=5)

        proj_ability_data_1 = AbilityData(
            250, projectile_label='bullet', projectile_count=1,
            kickback=200, spread=5)

        self.assertNotEqual(proj_ability_data_0, proj_ability_data_1)

        proj_ability_data_0 = AbilityData(
            250, projectile_label='bullet', projectile_count=1,
            kickback=200, spread=5)

        proj_ability_data_1 = AbilityData(
            250, projectile_label='bullet', projectile_count=1,
            kickback=200, spread=6)

        self.assertNotEqual(proj_ability_data_0, proj_ability_data_1)

        proj_ability_data_0 = AbilityData(
            250, projectile_label='bullet', projectile_count=1,
            kickback=200, spread=5, sound_on_use='a')

        proj_ability_data_1 = AbilityData(
            250, projectile_label='bullet', projectile_count=1,
            kickback=200, spread=5, sound_on_use='b')

        self.assertNotEqual(proj_ability_data_0, proj_ability_data_1)

        proj_ability_data_0 = AbilityData(
            250, projectile_label='bullet', projectile_count=1,
            kickback=200, spread=5)

        proj_ability_data_1 = AbilityData(
            250, projectile_label='little_bullet', projectile_count=1,
            kickback=200, spread=5)

        self.assertNotEqual(proj_ability_data_0, proj_ability_data_1)

import unittest
from typing import Tuple

import model
import mods
from abilities import EnergyAbility, ProjectileAbilityData, FireProjectile
from creatures.players import Player
from images import LITTLE_LASER
from projectiles import ProjectileData
from test.pygame_mock import initialize_pygame, initialize_gameobjects, \
    MockTimer
from tilemap import ObjectType
from src.test.testing_utilities import make_player, make_item


def setUpModule() -> None:
    initialize_pygame()
    initialize_gameobjects(LaserTest.groups, LaserTest.timer)

    projectile_data = ProjectileData(hits_player=False, damage=100,
                                     speed=1000,
                                     max_lifetime=1000,
                                     image_file=LITTLE_LASER,
                                     angled_image=True)
    ability_data = ProjectileAbilityData(500, projectile_data=projectile_data,
                                         projectile_count=1,
                                         kickback=0, spread=2,
                                         fire_effect=lambda x: None)
    LaserTest.laser_ability = FireProjectile(ability_data)


class LaserTest(unittest.TestCase):
    groups = model.Groups()
    timer = MockTimer()
    laser_ability = None

    def tearDown(self) -> None:
        self.groups.empty()
        self.timer.reset()

    def test_using_energy_ability_without_source_throws_error(self) -> None:
        ability = EnergyAbility(self.laser_ability, 10.0)

        expected_regex = 'An energy source must be '
        with self.assertRaisesRegex(RuntimeError, expected_regex):
            ability.can_use

        with self.assertRaisesRegex(RuntimeError, expected_regex):
            ability.use(make_player())

    def test_player_picks_up_laser_gun_gives_energy_source(self) -> None:
        player = make_player()
        laser_gun = make_item(ObjectType.LASER_GUN)

        fire_ability = laser_gun.mod.ability

        self.assertIsNone(fire_ability._energy_source)
        player.attempt_pickup(laser_gun)
        self.assertIsNotNone(fire_ability._energy_source)

    def test_player_fire_laser_available_after_cooldown_time(self) -> None:
        player = make_player()
        laser_gun = make_item(ObjectType.LASER_GUN)
        player.attempt_pickup(laser_gun)
        fire_ability = laser_gun.mod.ability

        self.assertFalse(fire_ability.can_use)
        # Initially player can't fire the gun because the cooldown time has
        # not been waited.
        while fire_ability.cooldown_fraction < 1:
            self.timer.current_time += 1
        self.assertFalse(fire_ability.can_use)

        self.timer.current_time += 1
        self.assertTrue(fire_ability.can_use)

    def test_player_fires_laser_makes_projectile(self) -> None:
        laser_gun, player = self._player_with_ready_laser()

        fire_laser = player.ability_caller(laser_gun.mod.loc)

        self.assertEqual(len(self.groups.bullets), 0)
        fire_laser()
        self.assertEqual(len(self.groups.bullets), 1)

    def test_player_fires_laser_expends_energy(self) -> None:
        laser_gun, player = self._player_with_ready_laser()

        starting_energy = player.energy_source.energy_available

        fire_laser = player.ability_caller(laser_gun.mod.loc)
        fire_laser()
        final_energy = player.energy_source.energy_available

        expected = laser_gun.mod.energy_required
        actual = starting_energy - final_energy
        self.assertEqual(actual, expected)

    def test_player_cannot_fire_laser_with_too_low_energy(self) -> None:
        laser_gun, player = self._player_with_ready_laser()

        self.assertTrue(laser_gun.mod.ability.can_use)

        all_energy = player.energy_source.energy_available
        player.energy_source.expend_energy(all_energy)

        self.assertFalse(laser_gun.mod.ability.can_use)

    def _player_with_ready_laser(self) -> Tuple[mods.ItemObject, Player]:
        player = make_player()
        laser_gun = make_item(ObjectType.LASER_GUN)
        player.attempt_pickup(laser_gun)
        fire_ability = laser_gun.mod.ability
        while fire_ability.cooldown_fraction < 1:
            self.timer.current_time += 10
        self.timer.current_time += 1
        return laser_gun, player


if __name__ == '__main__':
    unittest.main()

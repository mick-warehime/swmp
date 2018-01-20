import unittest
from typing import Tuple

import items
import model
from abilities import GenericAbility, AbilityData
from creatures.players import Player
from data.abilities_io import load_ability_data_kwargs
from src.test.testing_utilities import make_player, make_item
from test import dummy_audio_video
from test.pygame_mock import initialize_pygame, initialize_gameobjects, \
    MockTimer
from tilemap import ObjectType


def setUpModule() -> None:
    initialize_pygame()
    initialize_gameobjects(LaserTest.groups, LaserTest.timer)

    ability_data = AbilityData(**load_ability_data_kwargs('laser'))
    LaserTest.laser_ability = GenericAbility(ability_data)
    dummy_audio_video


class LaserTest(unittest.TestCase):
    groups = model.Groups()
    timer = MockTimer()
    laser_ability = None

    def tearDown(self) -> None:
        self.groups.empty()
        self.timer.reset()

    def test_player_fire_laser_available_after_cooldown_time(self) -> None:
        player = make_player()
        laser_gun = make_item(ObjectType.LASER_GUN)
        player.attempt_pickup(laser_gun)
        fire_ability = laser_gun.mod.ability

        self.assertFalse(fire_ability.can_use(player))
        # Initially player can't fire the gun because the cooldown time has
        # not been waited.
        while fire_ability.cooldown_fraction < 1:
            self.timer.current_time += 1
        self.assertFalse(fire_ability.can_use(player))

        self.timer.current_time += 1
        self.assertTrue(fire_ability.can_use(player))

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

        expected = load_ability_data_kwargs('laser')['energy_required']
        actual = starting_energy - final_energy
        self.assertEqual(actual, expected)

    def test_player_cannot_fire_laser_with_too_low_energy(self) -> None:
        laser_gun, player = self._player_with_ready_laser()

        self.assertTrue(laser_gun.mod.ability.can_use(player))

        all_energy = player.energy_source.energy_available
        player.energy_source.expend_energy(all_energy)

        self.assertFalse(laser_gun.mod.ability.can_use(player))

    def _player_with_ready_laser(self) -> Tuple[
        items.ItemObject, Player]:
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

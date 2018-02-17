import unittest

from model import Groups
from quests import resolutions
from quests.resolutions import MakeDecision
from test import pygame_mock, testing_utilities


def setUpModule() -> None:
    pygame_mock.initialize_pygame()

    groups = Groups()
    timer = pygame_mock.MockTimer()
    pygame_mock.initialize_gameobjects(groups, timer)


class ResolutionsTest(unittest.TestCase):
    def test_kill_group_starts_resolved(self) -> None:
        kill_group_data = {'kill group': {'group label': 'Mortys'}}
        kill_group = resolutions.resolution_from_data(kill_group_data)
        self.assertTrue(kill_group.is_resolved)

    def test_kill_group_resolved_after_death(self) -> None:
        kill_group = resolutions.KillGroup('Mortys')
        player = testing_utilities.make_player()
        sprite_labels = {'Mortys': {player}}

        kill_group.load_sprite_data(sprite_labels)

        self.assertFalse(kill_group.is_resolved)

        player.kill()
        self.assertTrue(kill_group.is_resolved)

    def test_enter_zone_resolved_after_collision(self) -> None:
        data = {'enter zone': {'zone label': 'collidee',
                               'entering label': 'collider'}}
        resolution = resolutions.resolution_from_data(data)

        player = testing_utilities.make_player()
        zombie = testing_utilities.make_zombie(player)

        labels = {'collidee': {zombie}, 'collider': {player}}
        resolution.load_sprite_data(labels)

        self.assertFalse(resolution.is_resolved)

        player.pos = zombie.pos
        self.assertTrue(resolution.is_resolved)

    def test_condition_satisfied_is_resolved(self) -> None:
        condition_data = {'damaged': None}
        res_data = {'condition': {'condition data': condition_data,
                                  'tested label': 'Morty'}}
        player = testing_utilities.make_player()
        labels = {'Morty': {player}}

        resolution = resolutions.resolution_from_data(res_data)
        resolution.load_sprite_data(labels)

        self.assertFalse(resolution.is_resolved)
        player.status.increment_health(-3)
        self.assertTrue(resolution.is_resolved)

    def test_condition_satisfied_too_many_labels_error(self) -> None:
        condition_data = {'damaged': None}
        res_data = {'condition': {'condition data': condition_data,
                                  'tested label': 'Morty'}}
        player = testing_utilities.make_player()
        labels = {'Morty': [player, player]}

        resolution = resolutions.resolution_from_data(res_data)
        with self.assertRaises(ValueError):
            resolution.load_sprite_data(labels)

    def test_make_decision_is_resolved_after_choice(self) -> None:
        res_data = {'decision choice': {'description': 'something'}}
        resolution: MakeDecision = resolutions.resolution_from_data(res_data)

        self.assertFalse(resolution.is_resolved)
        resolution.choose()
        self.assertTrue(resolution.is_resolved)

    def test_make_decision_str(self) -> None:
        res_data = {'decision choice': {'description': 'something'}}
        resolution: MakeDecision = resolutions.resolution_from_data(res_data)
        self.assertEqual(str(resolution), 'MakeDecision: something')

    def test_make_decision_null_load_data(self) -> None:
        res_data = {'decision choice': {'description': 'something'}}
        resolution: MakeDecision = resolutions.resolution_from_data(res_data)
        resolution.load_sprite_data({})

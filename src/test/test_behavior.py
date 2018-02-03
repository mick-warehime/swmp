import unittest

from pygame.surface import Surface

import model
from creatures.enemies import Behavior, Enemy, EnemyData
from data.input_output import load_npc_data_kwargs
from effects import TargetClose
from test import dummy_audio_video
from test.pygame_mock import initialize_pygame, initialize_gameobjects, \
    MockTimer
from test.testing_utilities import make_player


def setUpModule() -> None:
    initialize_pygame()
    initialize_gameobjects(HumanoidsTest.groups, HumanoidsTest.timer)
    dummy_audio_video


class HumanoidsTest(unittest.TestCase):
    groups = model.Groups()
    timer = MockTimer()

    def tearDown(self) -> None:
        self.groups.empty()
        self.timer.reset()

    def test_behavior_load_from_data_correct_state_conditions(self) -> None:
        player = make_player()
        fake_map = Surface(size=(10, 10))
        cond_val = 1
        behavior_dict = {
            'passive': {
                'conditions': ['default'],
                'effects': {}},
            'active': {
                'conditions': [
                    {'target close': {'threshold': 400, 'value': cond_val}}],
                'effects': {}},
            'dead': {
                'conditions': [
                    {'dead': {'value': 100}}],
                'effects': {}}
        }

        behavior = Behavior(behavior_dict, player, self.timer, fake_map)

        state_condition_values = behavior._state_condition_values

        states = set(state_condition_values.keys())
        expected = {'active', 'dead'}
        self.assertEqual(states, expected)

        expected_state = 'passive'
        self.assertEqual(behavior.default_state, expected_state)

        active_conditions = state_condition_values['active']
        key = next(iter(active_conditions.keys()))
        self.assertIsInstance(key, TargetClose)
        self.assertEqual(active_conditions[key], cond_val)

    def test_behavior_load_from_data_correct_effects(self) -> None:
        player = make_player()
        fake_map = Surface(size=(10, 10))

        behavior_dict = {
            'passive': {
                'conditions': ['default'],
                'effects': {
                    'stop motion': None
                }},
            'active': {
                'conditions': [
                    {'target close': {'threshold': 400, 'value': 1}}],
                'effects': {
                    'face and pursue target':
                        {'conditions': [{'dead': {'logical_not': None}},
                                        {'energy not full': None}]}
                }},
            'dead': {
                'conditions': [
                    {'dead': {'value': 100}}],
                'effects': {}}
        }

        behavior = Behavior(behavior_dict, player, self.timer, fake_map)

    def test_enemy_construction_with_behavior(self) -> None:
        player = make_player()

        enemy_data_dict = load_npc_data_kwargs('mob')
        enemy_data = EnemyData(**enemy_data_dict)
        Enemy(player.pos, player, enemy_data)

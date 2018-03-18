import unittest

from pygame.math import Vector2
from pygame.surface import Surface

import model
from creatures.enemies import Behavior, Enemy, EnemyData
from data.input_output import load_npc_data_kwargs
from conditions import TargetClose
from test.pygame_mock import initialize_pygame, initialize_gameobjects, \
    MockTimer
from test.testing_utilities import make_player


def setUpModule() -> None:
    initialize_pygame()
    initialize_gameobjects(HumanoidsTest.groups, HumanoidsTest.timer)


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

        behavior = Behavior(behavior_dict, player, self.timer)

        state_condition_values = behavior._state_conditions_values

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
                                        {'damaged': {'logical_not': None}}]}
                }},
            'dead': {
                'conditions': [
                    {'dead': {'value': 100}}],
                'effects': {
                    'kill': None
                }}
        }

        enemy_data = EnemyData(**load_npc_data_kwargs('zombie')).replace(
            behavior_dict=behavior_dict)

        enemy = Enemy(player.pos + Vector2(100, 0), player, enemy_data)

        self.assertEqual(enemy.status.state, 'passive')

        self.assertEqual(enemy.motion.vel, Vector2(0, 0))
        self.assertEqual(enemy.motion.rot, 0)
        enemy.update()
        self.assertEqual(enemy.status.state, 'active')
        self.assertLess(enemy.motion.vel.x, 0)
        self.assertAlmostEqual(enemy.motion.rot % 360, 180)

        enemy.status.increment_health(-enemy.status.max_health)
        self.assertEqual(len(self.groups.enemies), 1)
        enemy.update()
        self.assertEqual(enemy.status.state, 'dead')
        self.assertEqual(len(self.groups.enemies), 0)

    def test_enemy_construction_with_behavior(self) -> None:
        player = make_player()

        enemy_data_dict = load_npc_data_kwargs('zombie')
        enemy_data = EnemyData(**enemy_data_dict)
        Enemy(player.pos, player, enemy_data)

    def test_turret_behavior(self) -> None:
        player = make_player()

        enemy_data_dict = load_npc_data_kwargs('turret')
        enemy_data = EnemyData(**enemy_data_dict)
        turret = Enemy(player.pos + Vector2(100, 0), player, enemy_data)

        self.assertEqual(turret.status.state, 'passive')
        self.assertEqual(turret.motion.rot, 0)
        self.assertEqual(len(self.groups.enemy_projectiles), 0)

        turret.update()

        self.assertEqual(turret.status.state, 'active')
        self.assertAlmostEqual(turret.motion.rot % 360, 180)

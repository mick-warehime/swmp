import unittest

from parameterized import parameterized

import decision_controller
from quests.resolutions import MakeDecision
from test import pygame_mock


class DecisionControllerTest(unittest.TestCase):
    def setUp(self) -> None:
        pg = pygame_mock.Pygame()
        decision_controller.pg.mouse = pg.mouse
        decision_controller.pg.key = pg.key
        self.pressed_keys = [decision_controller.pg.K_1,
                             decision_controller.pg.K_2,
                             decision_controller.pg.K_3]

    @parameterized.expand([(0,), (1,), (2,)])
    def test_set_option_0(self, choice: int) -> None:
        prompt = 'Do you go into the swamp?'
        options = ['one', 'two', 'three']
        decisions = [MakeDecision(opt) for opt in options]
        dc = decision_controller.DecisionController(prompt, decisions)

        self.assertEqual(len(dc.resolved_resolutions()), 0)
        key = self.pressed_keys[choice]
        decision_controller.pg.key.pressed[key] = 1

        dc.update()

        self.assertEqual(len(dc.resolved_resolutions()), 1)
        self.assertIs(dc.resolved_resolutions()[0], decisions[choice])


if __name__ == '__main__':
    unittest.main()

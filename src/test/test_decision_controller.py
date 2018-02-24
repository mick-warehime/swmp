import unittest

from parameterized import parameterized

import controllers.base
from controllers import decision_controller
from quests.resolutions import MakeDecision
from test import pygame_mock


def setUpModule() -> None:
    controllers.base.initialize_controller(None, lambda x: x)


class DecisionControllerTest(unittest.TestCase):
    def setUp(self) -> None:
        pg = pygame_mock.Pygame()
        decision_controller.pg.mouse = pg.mouse
        decision_controller.pg.key = pg.key
        self.pressed_keys = [decision_controller.pg.K_1,
                             decision_controller.pg.K_2,
                             decision_controller.pg.K_3]

    def tearDown(self) -> None:
        controllers.base.Controller.keyboard.handle_input()

    @parameterized.expand([(0,), (1,), (2,)])
    def test_set_option_0(self, choice: int) -> None:
        prompt = 'Do you go into the swamp?'
        options = ['one', 'two', 'three']
        decisions = [MakeDecision(opt) for opt in options]
        dc = decision_controller.DecisionController(prompt, decisions)

        resolved_resolutions = [dec for dec in decisions if dec.is_resolved]
        self.assertEqual(len(resolved_resolutions), 0)
        key = self.pressed_keys[choice]
        decision_controller.pg.key.pressed[key] = 1

        dc.update()

        resolved_resolutions = [dec for dec in decisions if dec.is_resolved]
        self.assertEqual(len(resolved_resolutions), 1)
        self.assertIs(resolved_resolutions[0], decisions[choice])


if __name__ == '__main__':
    unittest.main()

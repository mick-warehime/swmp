import unittest
import decision_controller
from test import pygame_mock


class DecisionControllerTest(unittest.TestCase):
    def setUp(self) -> None:
        pg = pygame_mock.Pygame()
        decision_controller.pg.mouse = pg.mouse
        decision_controller.pg.key = pg.key

    def test_set_option_0(self) -> None:
        prompt = 'Do you go into the swamp?'
        options = ['one', 'two', 'three']
        dc = decision_controller.DecisionController(prompt, options)

        key0 = decision_controller.pg.K_1
        decision_controller.pg.key.pressed[key0] = 1

        dc.update()

        self.assertEqual(dc.choice, 0)

    def test_set_option_1(self) -> None:
        prompt = 'Do you go into the swamp?'
        options = ['one', 'two', 'three']
        dc = decision_controller.DecisionController(prompt, options)

        key1 = decision_controller.controller.pg.K_2
        decision_controller.pg.key.pressed[key1] = 1

        dc.update()

        self.assertEqual(dc.choice, 1)

    def test_set_option_2(self) -> None:
        prompt = 'Do you go into the swamp?'
        options = ['one', 'two', 'three']
        dc = decision_controller.DecisionController(prompt, options)

        key2 = decision_controller.controller.pg.K_3
        decision_controller.pg.key.pressed[key2] = 1

        dc.update()

        self.assertEqual(dc.choice, 2)

    def test_get_text(self) -> None:
        prompt = 'Do you go into the swamp?'
        options = ['one', 'two', 'three']
        dc = decision_controller.DecisionController(prompt, options)

        text = dc._get_texts()

        # ensure the text presents three options with the correct label
        for number in ['1', '2', '3']:
            self.assertTrue(any([number in el for el in text]))


if __name__ == '__main__':
    unittest.main()

import unittest
import pygame_mock
import sys
sys.modules['pygame'] = pygame_mock.Pygame()
import controller


class ControllerTest(unittest.TestCase):
    def test_set_functions(self) -> None:
        ctrl = controller.Controller()
        self.assertTrue(ctrl is not None)

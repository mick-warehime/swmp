import unittest

from test.pygame_mock import initialize_pygame
from view import sounds


def setUpModule() -> None:
    initialize_pygame()


class SoundTest(unittest.TestCase):
    def test_load_sounds(self) -> None:
        se = sounds.SoundEffects()
        self.assertTrue(se is not None)

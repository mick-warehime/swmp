import unittest
import sounds
from test.pygame_mock import initialize_pygame


def setUpModule() -> None:
    initialize_pygame()


class SoundTest(unittest.TestCase):
    def test_load_soudns(self) -> None:
        se = sounds.SoundEffects()
        self.assertTrue(se is not None)

import unittest

from pygame.sprite import Sprite

import model
from test.pygame_mock import initialize_pygame, initialize_gameobjects, \
    MockTimer


def setUpModule() -> None:
    initialize_pygame()
    initialize_gameobjects(ModelTest.groups, ModelTest.timer)


class ModelTest(unittest.TestCase):
    groups = model.Groups()
    timer = MockTimer()

    def tearDown(self)->None:
        self.groups.empty()

    def test_groups_which_in(self) -> None:
        groups = self.groups
        groups_added = [self.groups.bullets, self.groups.mobs]

        dummy_sprite = Sprite(*groups_added)

        groups_in = groups.which_in(dummy_sprite)

        self.assertEqual(set(groups_in), set(groups_added))


if __name__ == '__main__':
    unittest.main()

import unittest

from pygame.math import Vector2

import model

from src.test.pygame_mock import initialize_pygame, MockTimer
from data.constructors import build_map_object
from tilemap import ObjectType


def setUpModule() -> None:
    initialize_pygame()
    ConstructorTest.groups = model.Groups()
    model.initialize(ConstructorTest.groups, MockTimer())


class ConstructorTest(unittest.TestCase):
    groups = None

    def tearDown(self):
        self.groups.empty()

    def test_build_obstacle(self):
        self.assertEqual(len(self.groups.walls), 0)
        build_map_object(ObjectType.WALL, Vector2(0, 0), None, (30, 30))
        self.assertEqual(len(self.groups.walls), 1)

    def test_build_zone(self):
        self.assertEqual(len(self.groups.zones), 0)
        build_map_object(ObjectType.ZONE, Vector2(0, 0), None, (30, 30))
        self.assertEqual(len(self.groups.zones), 1)

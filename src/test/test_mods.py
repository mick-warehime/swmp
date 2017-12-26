import unittest
from typing import Callable
import os
from pygame.math import Vector2
import model
from mods import Mod, PistolObject
from src.test.pygame_mock import MockTimer, Pygame, initialize_pygame, \
    initialize_gameobjects

# This allows for running tests without actually generating a screen display
# or audio output.
os.environ['SDL_VIDEODRIVER'] = 'dummy'
os.environ['SDL_AUDIODRIVER'] = 'dummy'

pg = Pygame()


def setUpModule() -> None:
    initialize_pygame()
    initialize_gameobjects(ModTest.groups, ModTest.timer)


def _assert_runtime_exception_raised(tested_fun: Callable) -> None:
    exception_raised = False
    try:
        tested_fun()
    except RuntimeError:
        exception_raised = True
    assert exception_raised


class ModTest(unittest.TestCase):
    groups = model.Groups()
    timer = MockTimer()

    def tearDown(self) -> None:
        self.groups.empty()
        self.timer.reset()

    def test_mod_base_class_abstract_properties(self) -> None:
        mod_base = Mod()
        with self.assertRaises(NotImplementedError):
            mod_base.loc

        with self.assertRaises(NotImplementedError):
            mod_base.expended

        with self.assertRaises(NotImplementedError):
            mod_base.equipped_image

        with self.assertRaises(NotImplementedError):
            mod_base.backpack_image

    def test_item_object_bob_motion(self) -> None:
        pistol_item = PistolObject(Vector2(0, 0))
        time_for_sweep = int(pistol_item._bob_period * 10)

        center = pistol_item.rect.center
        original_center_y = center[1]
        original_center_x = center[0]
        min_center_y = center[1]
        max_center_y = center[1]

        for _ in range(time_for_sweep):
            min_center_y = min(min_center_y, center[1])
            max_center_y = max(max_center_y, center[1])
            self.assertEqual(center[1], original_center_x)

        self.assertEqual(original_center_y, min_center_y)
        self.assertEqual(-original_center_y, max_center_y)


if __name__ == '__main__':
    unittest.main()

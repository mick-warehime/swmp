import unittest
from pygame.math import Vector2
import model
from mods import Mod, PistolObject
from src.test.pygame_mock import MockTimer, initialize_pygame, \
    initialize_gameobjects


def setUpModule() -> None:
    initialize_pygame()
    initialize_gameobjects(ModTest.groups, ModTest.timer)


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

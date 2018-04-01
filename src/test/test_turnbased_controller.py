import unittest
from pygame import Rect
from src.test.pygame_mock import initialize_pygame
from src.test.testing_utilities import make_turnbased_controller


def setUpModule() -> None:
    initialize_pygame()


class TurnBasedControllerTest(unittest.TestCase):
    def test_create_and_draw(self) -> None:
        # ensures nothing crashes when drawing
        ctrl = make_turnbased_controller()
        ctrl._view._draw_debug = True
        ctrl.draw()

    def test_collide_line(self) -> None:
        ctrl = make_turnbased_controller()
        ctrl.draw()

        top_left = Rect(0, 0, 20, 20)
        top_right = Rect(1000, 0, 20, 20)
        bottom_left = Rect(0, 1000, 20, 20)
        bottom_right = Rect(1000, 1000, 20, 20)

        # The test level has a wall halfway down vertically
        self.assertFalse(ctrl._view._path_is_clear(top_left, top_right))
        self.assertFalse(ctrl._view._path_is_clear(top_right, top_left))

        self.assertTrue(ctrl._view._path_is_clear(top_right, bottom_right))
        self.assertTrue(ctrl._view._path_is_clear(bottom_right, top_right))

        self.assertTrue(ctrl._view._path_is_clear(top_left, bottom_left))
        self.assertTrue(ctrl._view._path_is_clear(bottom_left, top_left))

        self.assertTrue(ctrl._view._path_is_clear(bottom_right, bottom_left))
        self.assertTrue(ctrl._view._path_is_clear(bottom_left, bottom_right))

    def test_try_move_member(self) -> None:
        ctrl = make_turnbased_controller()
        ctrl.draw()

        self.assertFalse(ctrl._view._party.active_member_moved)

        # click the center of the first available move option
        r = ctrl._view._move_options[0]
        ctrl._view._try_move(r.center)

        # TODO - we should be checking if the active member moved
        # need to implement actions first
        self.assertIsNone(ctrl._view._move_options)
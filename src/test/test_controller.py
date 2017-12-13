import unittest
from . import pygame_mock
import sys

pg = pygame_mock.Pygame()

sys.modules['pygame'] = pg
import controller


class ControllerTest(unittest.TestCase):
    def setUp(self) -> None:
        self.a_key: int = 0
        self.b_key: int = 1
        self.c_key: int = 2
        self.a: str = ''
        self.b: str = ''
        self.c: str = ''
        self.d: str = ''
        self.e: str = ''

    def set_a(self, a: str) -> None:
        self.a = a

    def set_b(self, b: str) -> None:
        self.b = b

    def set_c(self, c: str) -> None:
        self.c = c

    def set_d(self, d: str) -> None:
        self.d = d

    def set_e(self, e: str) -> None:
        self.e = e

    def test_bind(self) -> None:
        ctrl = controller.Controller()

        test_string = 'set a'
        ctrl.bind(self.a_key, lambda: self.set_a(test_string))

        pg.key.pressed[self.a_key] = 1

        ctrl.update()
        self.assertEqual(self.a, test_string)

    def test_bind_down(self) -> None:
        ctrl = controller.Controller()

        test_string = 'set a'
        ctrl.bind_down(self.a_key, lambda: self.set_a(test_string))

        # function is called when you press the key
        pg.key.pressed[self.a_key] = 1
        ctrl.update()
        self.assertEqual(self.a, test_string)

        # reset to detect future calls
        self.a = ''

        # nothing happens if you keep it help down
        pg.key.pressed[self.a_key] = 1
        ctrl.update()
        self.assertEqual(self.a, '')

        # nothing happens when you release
        pg.key.pressed[self.a_key] = 0
        ctrl.update()
        self.assertEqual(self.a, '')

        # function called again when you press down
        pg.key.pressed[self.a_key] = 1
        ctrl.update()
        self.assertEqual(self.a, test_string)

    def test_mouse(self) -> None:
        ctrl = controller.Controller()

        test_string = 'set a'
        ctrl.bind_mouse(self.a_key, lambda: self.set_a(test_string))

        pg.mouse.pressed[self.a_key] = 1

        ctrl.update()
        self.assertEqual(self.a, test_string)

    def test_multiple_press(self) -> None:
        ctrl = controller.Controller()

        test_string_a = 'set a'
        test_string_b = 'set b'
        test_string_c = 'set c'

        test_mouse_1 = 'mouse 1'
        test_mouse_2 = 'mouse 2'

        ctrl.bind(self.a_key, lambda: self.set_a(test_string_a))
        ctrl.bind(self.b_key, lambda: self.set_b(test_string_b))
        ctrl.bind(self.c_key, lambda: self.set_c(test_string_c))
        ctrl.bind_mouse(self.a_key, lambda: self.set_d(test_mouse_1))
        ctrl.bind_mouse(self.b_key, lambda: self.set_e(test_mouse_2))

        # every combination of 3 keys and two mouse presses
        off_on = [0,1]
        for key_1 in off_on:
            for key_2 in off_on:
                for key_3 in off_on:
                    for mouse_1 in off_on:
                        for mouse_2 in off_on:

                            # press the keys
                            pg.key.pressed[0] = key_1
                            pg.key.pressed[1] = key_2
                            pg.key.pressed[2] = key_3
                            pg.mouse.pressed[0] = mouse_1
                            pg.mouse.pressed[1] = mouse_2

                            # update the controller
                            ctrl.update()

                            if key_1 == 1:
                                self.assertEqual(self.a, test_string_a)
                            if key_2 == 1:
                                self.assertEqual(self.b, test_string_b)
                            if key_3 == 1:
                                self.assertEqual(self.c, test_string_c)
                            if mouse_1 == 1:
                                self.assertEqual(self.d, test_mouse_1)
                            if mouse_2 == 1:
                                self.assertEqual(self.e, test_mouse_2)

                            # reset to register the next clicks
                            self.a = ''
                            self.b = ''
                            self.c = ''
                            self.d = ''
                            self.e = ''

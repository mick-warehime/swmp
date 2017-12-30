import unittest
from itertools import product
import controller
from test import pygame_mock


class ControllerTest(unittest.TestCase):
    def setUp(self) -> None:
        pg = pygame_mock.Pygame()
        controller.pg.mouse = pg.mouse
        controller.pg.key = pg.key

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
        n_default = ctrl.n_default_bindings

        test_string = 'set a'
        ctrl.bind(self.a_key, lambda: self.set_a(test_string))

        controller.pg.key.pressed[self.a_key] = 1

        # test we set the key
        self.assertEqual(len(ctrl.bindings), 1 + n_default)

        # ensure we haven't changed this yet
        self.assertEqual(self.a, '')

        ctrl.handle_input()
        self.assertEqual(self.a, test_string)

    def test_bind_down(self) -> None:
        ctrl = controller.Controller()

        test_string = 'set a'
        ctrl.bind_down(self.a_key, lambda: self.set_a(test_string))

        # function is called when you press the key
        controller.pg.key.pressed[self.a_key] = 1
        ctrl.handle_input()
        ctrl.set_previous_input()
        self.assertEqual(self.a, test_string)

        # reset to detect future calls
        self.a = ''

        # nothing happens if you keep it help down
        controller.pg.key.pressed[self.a_key] = 1
        ctrl.handle_input()
        ctrl.set_previous_input()
        self.assertEqual(self.a, '')

        # nothing happens when you release
        controller.pg.key.pressed[self.a_key] = 0
        ctrl.handle_input()
        ctrl.set_previous_input()
        self.assertEqual(self.a, '')

        # function called again when you press down
        controller.pg.key.pressed[self.a_key] = 1
        ctrl.handle_input()
        ctrl.set_previous_input()
        self.assertEqual(self.a, test_string)

    def test_mouse(self) -> None:
        ctrl = controller.Controller()

        test_string = 'set a'
        ctrl.bind_mouse(self.a_key, lambda: self.set_a(test_string))

        controller.pg.mouse.pressed[self.a_key] = 1

        ctrl.handle_input()
        self.assertEqual(self.a, test_string)

    def test_multiple_press(self) -> None:
        ctrl = controller.Controller()
        n_default = ctrl.n_default_bindings

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

        self.assertEqual(len(ctrl.bindings), 3 + n_default)
        self.assertEqual(len(ctrl.mouse_bindings), 2)

        # every combination of 3 keys and two mouse presses
        for key_1, key_2, key_3, mouse_1, mouse_2 in product(*[[0, 1]] * 5):
            # press the keys
            controller.pg.key.pressed[0] = key_1
            controller.pg.key.pressed[1] = key_2
            controller.pg.key.pressed[2] = key_3
            controller.pg.mouse.pressed[0] = mouse_1
            controller.pg.mouse.pressed[1] = mouse_2

            # .handle_input() combinations
            ctrl.handle_input()

            if key_1:
                self.assertEqual(self.a, test_string_a)
            if key_2:
                self.assertEqual(self.b, test_string_b)
            if key_3:
                self.assertEqual(self.c, test_string_c)
            if mouse_1:
                self.assertEqual(self.d, test_mouse_1)
            if mouse_2:
                self.assertEqual(self.e, test_mouse_2)

            # reset to register the next clicks
            self.a = ''
            self.b = ''
            self.c = ''
            self.d = ''
            self.e = ''

    def test_only_handle(self) -> None:
        ctrl = controller.Controller()
        n_default = ctrl.n_default_bindings

        test_string_a = 'set a'
        test_string_b = 'set b'
        test_string_c = 'set c'

        ctrl.bind(self.a_key, lambda: self.set_a(test_string_a))
        ctrl.bind(self.b_key, lambda: self.set_b(test_string_b))
        ctrl.bind(self.c_key, lambda: self.set_c(test_string_c))

        # test we set the key
        self.assertEqual(len(ctrl.bindings), 3 + n_default)

        # ensure we haven't changed this yet
        self.assertEqual(self.b, '')

        controller.pg.key.pressed[self.b_key] = 1
        ctrl.handle_input()
        self.assertEqual(self.b, test_string_b)

        controller.pg.key.pressed[self.c_key] = 1
        ctrl.handle_input()
        self.assertEqual(self.c, test_string_c)

        self.a = ''
        self.b = ''
        self.c = ''

        controller.pg.key.pressed[self.a_key] = 1
        controller.pg.key.pressed[self.b_key] = 1
        controller.pg.key.pressed[self.c_key] = 1
        ctrl.handle_input(only_handle=[self.a_key])
        self.assertEqual(self.a, test_string_a)
        self.assertEqual(self.b, '')
        self.assertEqual(self.c, '')


if __name__ == '__main__':
    unittest.main()

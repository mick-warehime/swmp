import unittest
from itertools import product
import controllers.base
from test import pygame_mock

import pygame


class KeyboardTest(unittest.TestCase):
    def setUp(self) -> None:
        pg = pygame_mock.Pygame()
        pygame.mouse = pg.mouse
        pygame.key = pg.key

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
        keyboard = controllers.base.Keyboard()

        n_bindings = len(keyboard._bindings)

        test_string = 'set a'
        keyboard.bind(self.a_key, lambda: self.set_a(test_string))

        pygame.key.pressed[self.a_key] = 1

        # test we set the key
        self.assertEqual(len(keyboard._bindings), 1 + n_bindings)

        # ensure we haven't changed this yet
        self.assertEqual(self.a, '')

        keyboard.handle_input()
        self.assertEqual(self.a, test_string)

    def test_bind_down(self) -> None:
        keyboard = controllers.base.Keyboard()

        test_string = 'set a'
        keyboard.bind_on_press(self.a_key, lambda: self.set_a(test_string))

        # function is called when you press the key
        pygame.key.pressed[self.a_key] = 1
        keyboard.handle_input()
        self.assertEqual(self.a, test_string)

        # reset to detect future calls
        self.a = ''

        # nothing happens if you keep it help down
        pygame.key.pressed[self.a_key] = 1
        keyboard.handle_input()
        self.assertEqual(self.a, '')

        # nothing happens when you release
        pygame.key.pressed[self.a_key] = 0
        keyboard.handle_input()
        self.assertEqual(self.a, '')

        # function called again when you press down
        pygame.key.pressed[self.a_key] = 1
        keyboard.handle_input()
        self.assertEqual(self.a, test_string)

    def test_mouse(self) -> None:
        keyboard = controllers.base.Keyboard()

        test_string = 'set a'
        keyboard.bind_mouse(self.a_key, lambda: self.set_a(test_string))

        pygame.mouse.pressed[self.a_key] = 1

        keyboard.handle_input()
        self.assertEqual(self.a, test_string)

    def test_multiple_press(self) -> None:
        keyboard = controllers.base.Keyboard()
        n_bindings = len(keyboard._bindings)

        test_string_a = 'set a'
        test_string_b = 'set b'
        test_string_c = 'set c'

        test_mouse_1 = 'mouse 1'
        test_mouse_2 = 'mouse 2'

        keyboard.bind(self.a_key, lambda: self.set_a(test_string_a))
        keyboard.bind(self.b_key, lambda: self.set_b(test_string_b))
        keyboard.bind(self.c_key, lambda: self.set_c(test_string_c))
        keyboard.bind_mouse(self.a_key, lambda: self.set_d(test_mouse_1))
        keyboard.bind_mouse(self.b_key, lambda: self.set_e(test_mouse_2))

        self.assertEqual(len(keyboard._bindings), 3 + n_bindings)
        self.assertEqual(len(keyboard._mouse_bindings), 2)

        # every combination of 3 keys and two mouse presses
        for key_1, key_2, key_3, mouse_1, mouse_2 in product(*[[0, 1]] * 5):
            # press the keys
            pygame.key.pressed[0] = key_1
            pygame.key.pressed[1] = key_2
            pygame.key.pressed[2] = key_3
            pygame.mouse.pressed[0] = mouse_1
            pygame.mouse.pressed[1] = mouse_2

            # .handle_input() combinations
            keyboard.handle_input()

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

            pygame.key.pressed[0] = 0
            pygame.key.pressed[1] = 0
            pygame.key.pressed[2] = 0
            pygame.mouse.pressed[0] = 0
            pygame.mouse.pressed[1] = 0

            keyboard.handle_input()

            # reset to register the next clicks
            self.a = ''
            self.b = ''
            self.c = ''
            self.d = ''
            self.e = ''

    def test_only_handle(self) -> None:
        keyboard = controllers.base.Keyboard()
        n_bindings = len(keyboard._bindings)

        test_string_a = 'set a'
        test_string_b = 'set b'
        test_string_c = 'set c'

        keyboard.bind(self.a_key, lambda: self.set_a(test_string_a))
        keyboard.bind(self.b_key, lambda: self.set_b(test_string_b))
        keyboard.bind(self.c_key, lambda: self.set_c(test_string_c))

        # test we set the key
        self.assertEqual(len(keyboard._bindings), 3 + n_bindings)

        # ensure we haven't changed this yet
        self.assertEqual(self.b, '')

        pygame.key.pressed[self.b_key] = 1
        keyboard.handle_input()
        self.assertEqual(self.b, test_string_b)

        pygame.key.pressed[self.c_key] = 1
        keyboard.handle_input()
        self.assertEqual(self.c, test_string_c)

        self.a = ''
        self.b = ''
        self.c = ''

        pygame.key.pressed[self.a_key] = 1
        pygame.key.pressed[self.b_key] = 1
        pygame.key.pressed[self.c_key] = 1
        keyboard.handle_input(allowed_keys=[self.a_key])
        self.assertEqual(self.a, test_string_a)
        self.assertEqual(self.b, '')
        self.assertEqual(self.c, '')


if __name__ == '__main__':
    unittest.main()

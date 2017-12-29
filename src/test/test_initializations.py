import unittest
from typing import Callable

import pygame

import creatures.mobs
import model
from abilities import CoolDownAbility
from creatures import humanoids as hmn
from src.test.pygame_mock import MockTimer, initialize_pygame
from src.test.testing_utilities import make_player, make_mob


def setUpModule() -> None:
    initialize_pygame()
    _initialization_tests()


def _initialization_tests() -> None:
    # Normally I would be running unit tests, but it is not possible to check
    #  exceptions once the classes are initialized.
    _assert_runtime_exception_raised(make_player)
    model.GameObject.initialize_gameobjects(InitsTest.groups)
    _assert_runtime_exception_raised(make_player)
    model.DynamicObject.initialize_dynamic_objects(InitsTest.timer)
    _assert_runtime_exception_raised(make_mob)
    blank_screen = pygame.Surface((800, 600))
    creatures.mobs.Mob.init_class(blank_screen)
    _assert_runtime_exception_raised(CoolDownAbility)
    CoolDownAbility.initialize_class(InitsTest.timer)

    InitsTest.groups.empty()
    InitsTest.timer.reset()


def _assert_runtime_exception_raised(tested_fun: Callable) -> None:
    exception_raised = False
    try:
        tested_fun()
    except RuntimeError:
        exception_raised = True
    assert exception_raised, 'Expected a RuntimeError to be raised for ' \
                             'function call %s' % (tested_fun,)


class InitsTest(unittest.TestCase):
    groups = model.Groups()
    timer = MockTimer()

    def tearDown(self) -> None:
        self.groups.empty()
        self.timer.reset()

    def test_pass(self) -> None:
        pass


if __name__ == '__main__':
    unittest.main()
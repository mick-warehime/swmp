import unittest
from typing import Union, Tuple, Callable
import os
from pygame.math import Vector2
import pygame
from pygame.sprite import Group, LayeredUpdates
import model
import humanoids as hmn
from abilities import FirePistol, CoolDownAbility
from mods import ShotgunMod
from src.test.pygame_mock import MockTimer, Pygame, initialize_pygame
from weapons import Bullet
from itertools import product
import math

# This allows for running tests without actually generating a screen display
# or audio output.
os.environ['SDL_VIDEODRIVER'] = 'dummy'
os.environ['SDL_AUDIODRIVER'] = 'dummy'

pg = Pygame()


def _make_player() -> hmn.Player:
    pos = pygame.math.Vector2(0, 0)
    player = hmn.Player(pos)
    return player


def _make_mob(player: Union[hmn.Player, None] = None,
              pos: Union[Vector2, None] = None) -> hmn.Mob:
    if player is None:
        player = _make_player()
    if pos is None:
        pos = player.pos + pygame.math.Vector2(100, 0)
    return hmn.Mob(pos, player, is_quest=False)


def setUpModule() -> None:
    initialize_pygame()
    _initialization_tests()


def _initialization_tests() -> None:
    # Normally I would be running unit tests, but it is not possible to check
    #  exceptions once the classes are initialized.
    _assert_runtime_exception_raised(_make_player)
    model.GameObject.initialize_gameobjects(InitsTest.groups)
    _assert_runtime_exception_raised(_make_player)
    model.DynamicObject.initialize_dynamic_objects(InitsTest.timer)
    _assert_runtime_exception_raised(_make_mob)
    blank_screen = pygame.Surface((800, 600))
    hmn.Mob.init_class(blank_screen)
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

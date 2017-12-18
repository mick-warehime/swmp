import unittest
from typing import Union
import sys, os

sys.path.append('../../')
sys.path.append('../')
sys.path.append('.')
import pygame
from pygame.sprite import Group, LayeredUpdates
import model
import humanoid as hmn
import images
import sounds
from src.test.pygame_mock import MockTimer, Pygame
from weapon import Weapon

# This allows for running tests without actually generating a screen display
# or audio output.
os.environ['SDL_VIDEODRIVER'] = 'dummy'
os.environ['SDL_AUDIODRIVER'] = 'dummy'

pg = Pygame()


def setUpModule() -> None:
    pygame.display.set_mode((600, 400))
    pygame.mixer.pre_init(44100, -16, 4, 2048)
    pygame.init()
    images.initialize_images()
    sounds.initialize_sounds()


def _make_weapon(label: str) -> Weapon:
    groups = model.Groups()
    timer = MockTimer()
    weapon = Weapon(label, timer, groups)
    return weapon


def _make_player(timer: Union[None, MockTimer] = None,
                 groups: Union[None, model.Groups] = None) -> hmn.Player:
    if groups is None:
        groups = model.Groups()
    if timer is None:
        timer = MockTimer()
    pos = pygame.math.Vector2(0, 0)
    player = hmn.Player(groups, timer, pos)
    player.set_weapon('pistol')
    return player


class ModTest(unittest.TestCase):


    def test_player_has_pistol(self) -> None:
        groups = model.Groups()
        timer = MockTimer()
        player = _make_player(timer=timer, groups=groups)

        self.assertEqual(len(groups.bullets), 0)
        player.shoot()
        self.assertEqual(len(groups.bullets), 0)
        timer.time += player._weapon.shoot_rate + 1
        player.shoot()
        self.assertEqual(len(groups.bullets), 1)


if __name__ == '__main__':
    unittest.main()

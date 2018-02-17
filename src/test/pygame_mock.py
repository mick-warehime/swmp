import os
from typing import List

import pygame

import abilities
import creatures.enemies
import images
import model
import sounds


class Key(object):
    def __init__(self, n_keys: int) -> None:
        self.pressed = [0] * n_keys

    def get_pressed(self) -> List[int]:
        return self.pressed


class Pygame(object):
    def __init__(self) -> None:
        self.key = Key(n_keys=500)
        self.mouse = Key(n_keys=500)


class MockTimer(model.Timer):
    def __init__(self) -> None:
        self._time = 0

    @property
    def current_time(self) -> int:
        return self._time

    @current_time.setter
    def current_time(self, new_time: int) -> None:
        self._time = new_time

    @property
    def dt(self) -> float:
        return 0.1

    def reset(self) -> None:
        self._time = 0


def initialize_pygame() -> None:
    try:
        pygame.display.set_mode((600, 400))
        pygame.mixer.pre_init(44100, -16, 4, 2048)
        pygame.init()

    except pygame.error:
        os.environ['SDL_VIDEODRIVER'] = 'dummy'
        os.environ['SDL_AUDIODRIVER'] = 'dummy'
        pygame.display.set_mode((600, 400))
        pygame.mixer.pre_init(44100, -16, 4, 2048)
        pygame.init()

    images.initialize_images()
    sounds.initialize_sounds()



def initialize_gameobjects(groups: model.Groups, timer: model.Timer) -> None:
    model.GameObject.initialize_gameobjects(groups)
    model.DynamicObject.initialize_dynamic_objects(timer)
    blank_screen = pygame.Surface((800, 600))
    creatures.enemies.Enemy.init_class(blank_screen)
    abilities.initialize_classes(timer)

import random
from typing import List

import model


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

    @property
    def dt(self) -> float:
        return 0.1

    def reset(self) -> None:
        self._time = 0

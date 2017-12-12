from typing import List


class Key(object):
    def __init__(self, n_keys: int) -> None:
        self.pressed = [0] * n_keys

    def get_pressed(self) -> List[int]:
        return self.pressed


class Pygame(object):
    def __init__(self) -> None:
        self.key = Key(n_keys=5)

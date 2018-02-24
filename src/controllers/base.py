from typing import Any

import pygame as pg

from controllers.keyboards import Keyboard
from creatures.humanoids import HumanoidData


def initialize_controller(screen: pg.Surface,
                          quit_func: Any) -> None:
    Controller._screen = screen
    Controller.keyboard = Keyboard()
    Keyboard.quit_func = quit_func


class Controller(object):
    _screen = None
    keyboard: Keyboard = None

    def __init__(self) -> None:
        self.keyboard.reset_bindings()

    def set_player_data(self, data: HumanoidData) -> None:
        raise NotImplementedError

    def draw(self) -> None:
        raise NotImplementedError

    def update(self) -> None:
        raise NotImplementedError

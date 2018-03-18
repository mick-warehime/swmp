from typing import Any

from controllers.keyboards import Keyboard
from creatures.humanoids import HumanoidData


def initialize_controller(quit_func: Any) -> None:
    Controller.keyboard = Keyboard()
    Keyboard.quit_func = quit_func


class Controller(object):
    keyboard: Keyboard = None

    def __init__(self) -> None:
        self.keyboard.reset_bindings()

    def set_player_data(self, data: HumanoidData) -> None:
        raise NotImplementedError

    def draw(self) -> None:
        raise NotImplementedError

    def update(self) -> None:
        raise NotImplementedError

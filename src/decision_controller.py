import controller
from typing import Dict, Callable
import pygame as pg


class DecisionController(controller.Controller):
    def __init__(self, prompt: str) -> None:

        super(DecisionController, self).__init__()

        self.options: Dict[int, str] = {}
        self.prompt = prompt
        self.choice = -1
        self.options_keys = [pg.K_0, pg.K_1, pg.K_2,
                             pg.K_3, pg.K_4, pg.K_5,
                             pg.K_6, pg.K_7, pg.K_8,
                             pg.K_9]

    def set_option(self, idx: int, option: str) -> None:

        assert idx < 10, 'decision must have less than 10 options'
        assert idx >= 0, 'decision must be a >= 0'

        key = self.options_keys[idx]
        self.bind(key, self.get_choice_function(idx))
        self.options[idx] = option

    def get_choice_function(self, key_idx: int) -> Callable[..., None]:
        def choice_func() -> None:
            self.choice = key_idx
        return choice_func

    def set_choice(self, choice: int) -> None:
        self.choice = choice

    def update(self) -> None:
        self.handle_input()

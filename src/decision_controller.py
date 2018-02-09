from typing import Callable, List

import pygame as pg

import controller
from view import DecisionView

_key_labels = [pg.K_1, pg.K_2, pg.K_3, pg.K_4, pg.K_5, pg.K_6, pg.K_7, pg.K_8,
               pg.K_9, pg.K_0]


class DecisionController(controller.Controller):
    # takes a list of strings of the form [Prompt, option 1, ..., option n]
    def __init__(self, prompt: str, options: List[str]) -> None:

        super().__init__()

        self._view = DecisionView(self._screen, prompt, options)
        self.choice = None
        self._allowed_keys = _key_labels + [pg.K_ESCAPE]
        for choice, key in enumerate(_key_labels):
            self.keyboard.bind(key, self._choice_function(choice))

    def update(self) -> None:

        self.keyboard.handle_input(allowed_keys=self._allowed_keys)

    def draw(self) -> None:
        self._view.draw()

    def _choice_function(self, choice: int) -> Callable[[], None]:
        def choice_func() -> None:
            self.choice = choice

        return choice_func

    def wait_for_decision(self) -> None:
        self.draw()
        while self.choice is None:
            pg.event.wait()
            self.update()

    def resolved_conflict_index(self) -> int:
        return self.choice

    # can't lose from decision screen
    def game_over(self) -> bool:
        return False

    def should_exit(self) -> bool:
        return self.choice is not None

        # decision controllers should take the option dict
        # dungeon controllers should take the next scene name as a param
        # all controllers should implement a function called next scene name

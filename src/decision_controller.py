from typing import List

import pygame as pg

import controller
from creatures.humanoids import HumanoidData
from quests.resolutions import MakeDecision, Resolution
from view import DecisionView

_key_labels = [pg.K_1, pg.K_2, pg.K_3, pg.K_4, pg.K_5, pg.K_6, pg.K_7, pg.K_8,
               pg.K_9, pg.K_0]


class DecisionController(controller.Controller):
    """Handles interactions between DecisionView, Resolutions, and user.
    """

    def __init__(self, prompt: str, decisions: List[MakeDecision]) -> None:
        super().__init__()

        self._decisions = decisions
        options = [decision.description for decision in decisions]
        self._view = DecisionView(self._screen, prompt, options)

        self._player_data: HumanoidData = None

        self._allowed_keys = _key_labels + [pg.K_ESCAPE]

        for decision, key in zip(self._decisions, _key_labels):
            self.keyboard.bind_on_press(key, decision.choose)

    def update(self) -> None:
        self.keyboard.handle_input(allowed_keys=self._allowed_keys)

    def draw(self) -> None:
        self._view.draw()

    def set_player_data(self, data: HumanoidData) -> None:
        self._player_data = data

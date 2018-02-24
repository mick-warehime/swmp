import pygame as pg

import controllers.base
from creatures.humanoids import HumanoidData
from quests.resolutions import MakeDecision
from view import DecisionView


class TransitionController(controllers.base.Controller):
    """Handles transitions, which involves basic user input and text drawing.
    """

    def __init__(self, description: str, continue_dec: MakeDecision) -> None:
        super().__init__()

        self._view = DecisionView(self._screen, description,
                                  ['press space to continue'],
                                  enumerate_options=False)

        self._player_data: HumanoidData = None

        self._allowed_keys = [pg.K_SPACE, pg.K_ESCAPE]

        self.keyboard.bind_on_press(pg.K_SPACE, continue_dec.choose)

    def update(self) -> None:
        self.keyboard.handle_input(allowed_keys=self._allowed_keys)

    def draw(self) -> None:
        self._view.draw()

    def set_player_data(self, data: HumanoidData) -> None:
        self._player_data = data

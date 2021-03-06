import pygame as pg

import controllers.base
from creatures.humanoids import HumanoidData
from items import ItemObject
from quests.resolutions import MakeDecision
from view.decision_view import DecisionView


class TransitionController(controllers.base.Controller):
    """Handles transitions, which involves basic user input and text drawing.
    """

    def __init__(self, description: str, continue_dec: MakeDecision,
                 gained_item: ItemObject = None) -> None:
        super().__init__()

        self._view = DecisionView(description, ['press space to continue'],
                                  enumerate_options=False)

        self._gained_item = gained_item

        self._player_data: HumanoidData = None

        self._allowed_keys = [pg.K_SPACE, pg.K_ESCAPE]

        self.keyboard.bind_on_press(pg.K_SPACE, continue_dec.choose)

    def update(self) -> None:
        self.keyboard.handle_input(allowed_keys=self._allowed_keys)

    def draw(self) -> None:
        self._view.draw()

    def set_player_data(self, data: HumanoidData) -> None:
        self._player_data = data
        if self._gained_item is not None:
            self._player_data.inventory.attempt_pickup(self._gained_item)
            # Even if the gained item is not picked up, it should be removed
            #  from Groups.
            self._gained_item.kill()
            self._gained_item = None

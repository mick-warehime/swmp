from controllers.transition_controller import TransitionController
from data import constructors
from quests.resolutions import MakeDecision
from quests.scenes.interface import ControllerAndResolutions, Scene


class TransitionScene(Scene):
    def __init__(self, description: str, gained_item_label: str = None) -> \
            None:
        self._description = description
        self._gained_item_label: str = gained_item_label

    def make_controller_and_resolutions(self) -> ControllerAndResolutions:
        continue_decision = MakeDecision('continue')
        if self._gained_item_label is not None:
            gained_item = constructors.build_map_object(
                self._gained_item_label)
        else:
            gained_item = None
        ctrl = TransitionController(self._description, continue_decision,
                                    gained_item)
        return ctrl, [continue_decision]

from controllers.transition_controller import TransitionController
from quests.resolutions import MakeDecision
from quests.scenes.interface import ControllerAndResolutions, Scene


class TransitionScene(Scene):
    def __init__(self, description: str) -> None:
        self._description = description

    def make_controller_and_resolutions(self) -> ControllerAndResolutions:
        continue_decision = MakeDecision('continue')
        ctrl = TransitionController(self._description, continue_decision)
        return ctrl, [continue_decision]

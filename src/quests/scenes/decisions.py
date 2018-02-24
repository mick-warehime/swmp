from typing import List, Dict

from controllers.decision_controller import DecisionController
from quests.resolutions import MakeDecision
from quests.scenes.interface import ControllerAndResolutions, Scene


class DecisionScene(Scene):
    def __init__(self, prompt: str,
                 decision_data: List[Dict[str, Dict[str, str]]]) -> None:
        self._prompt = prompt
        data = [list(dec.values())[0] for dec in decision_data]
        self._decisions = [dec['description'] for dec in data]

    def make_controller_and_resolutions(self) -> ControllerAndResolutions:
        resolutions = [MakeDecision(dec) for dec in self._decisions]
        ctrl = DecisionController(self._prompt, resolutions)
        return ctrl, resolutions

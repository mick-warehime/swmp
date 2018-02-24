from typing import Dict

from controllers.skill_check_controller import SkillCheckController, \
    DifficultyRating
from quests.resolutions import MakeDecision
from quests.scenes.interface import Scene, ControllerAndResolutions


class SkillCheckScene(Scene):
    def __init__(self, success_data: Dict[str, str],
                 failure_data: Dict[str, str], difficulty: str) -> None:
        self._success_description = success_data['description']
        self._failure_description = failure_data['description']
        self._difficulty = DifficultyRating(difficulty)

    def make_controller_and_resolutions(self) -> ControllerAndResolutions:
        success = MakeDecision(self._success_description)
        failure = MakeDecision(self._failure_description)

        ctrl = SkillCheckController(success, failure, self._difficulty)
        return ctrl, [success, failure]

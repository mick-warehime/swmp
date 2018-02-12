from enum import Enum
from typing import NamedTuple, List, Iterable, Tuple

from conditions import IsDead
from controller import Controller
from creatures.players import Player
from decision_controller import DecisionController
from dungeon_controller import DungeonController, Dungeon
from quests.resolutions import Resolution, MakeDecision, KillGroup, \
    ConditionSatisfied, EnterZone


class SceneType(Enum):
    DUNGEON = 'dungeon'
    DECISION = 'decision'


class BaseSceneData(NamedTuple):
    type: SceneType
    description: str
    # resolutions: List[Resolution]
    map_file: str


class SceneData(BaseSceneData):
    def __new__(cls, type_str: str, description: str,
                map_file: str = None) -> BaseSceneData:
        scene_type = SceneType(type_str)

        return super().__new__(cls, scene_type, description, map_file)


ControllerAndResolutions = Tuple[Controller, List[Resolution]]


class Scene(object):
    """Instantiates a controller to represent a scene.

    These are like factory methods for Controllers.
    """

    def make_controller_and_resolutions(self) -> ControllerAndResolutions:
        raise NotImplementedError


# def __init__(self, data: SceneData) -> None:
#     self.description = data.description
#     if data.scene_type == SceneType.DUNGEON:
#         assert data.map_file is not None
#         self.controller = DungeonController(data.map_file)


class DecisionScene(Scene):
    def __init__(self, prompt: str, decisions: List[str]) -> None:
        self._prompt = prompt
        self._decisions = decisions

    def make_controller_and_resolutions(self) -> ControllerAndResolutions:
        resolutions = [MakeDecision(dec) for dec in self._decisions]
        ctrl = DecisionController(self._prompt, resolutions)
        return ctrl, resolutions


class DungeonScene(Scene):
    def __init__(self, map_file: str):
        self._map_file = map_file

    def make_controller_and_resolutions(self) -> ControllerAndResolutions:
        dungeon = Dungeon(self._map_file)
        sprite_labels = dungeon.labeled_sprites

        # For now these are fixed and not defined from data.
        kill_quest = KillGroup('quest')
        player_dead = ConditionSatisfied('player', IsDead())
        enter_waypoint = EnterZone('exit', 'player')

        resolutions = [kill_quest, player_dead, enter_waypoint]

        for resolution in resolutions:
            resolution.load_data(sprite_labels)

        return DungeonController(dungeon), resolutions
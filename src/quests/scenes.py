from enum import Enum
from typing import NamedTuple, List, Tuple, Dict, Any

from controller import Controller
from decision_controller import DecisionController
from dungeon_controller import DungeonController, Dungeon
from quests.resolutions import Resolution, MakeDecision, resolution_from_data


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


class DecisionScene(Scene):
    def __init__(self, prompt: str, decisions: List[str]) -> None:
        self._prompt = prompt
        self._decisions = decisions

    def make_controller_and_resolutions(self) -> ControllerAndResolutions:
        resolutions = [MakeDecision(dec) for dec in self._decisions]
        ctrl = DecisionController(self._prompt, resolutions)
        return ctrl, resolutions


class DungeonScene(Scene):
    def __init__(self, map_file: str, resolution_datas: List[Dict]):
        self._map_file = map_file

        self._resolution_datas = resolution_datas

    def make_controller_and_resolutions(self) -> ControllerAndResolutions:
        dungeon = Dungeon(self._map_file)
        sprite_labels = dungeon.labeled_sprites

        resolutions = [resolution_from_data(data) for data in
                       self._resolution_datas]

        for resolution in resolutions:
            resolution.load_sprite_data(sprite_labels)

        return DungeonController(dungeon), resolutions


def make_scene(scene_data: Dict[str, Any]) -> Scene:
    scene_type = SceneType(scene_data['type'])

    if scene_type == SceneType.DUNGEON:
        return DungeonScene(scene_data['map file'], scene_data['resolutions'])
    else:
        assert scene_type == SceneType.DECISION
        choices = [list(dct.keys())[0] for dct in scene_data['choices']]
        return DecisionScene(scene_data['prompt'], choices)

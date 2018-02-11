from enum import Enum
from typing import NamedTuple, List, Iterable

from controller import Controller
from creatures.players import Player
from dungeon_controller import DungeonController
from quests.resolutions import Resolution


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


class Scene(object):
    def __init__(self, data: SceneData) -> None:
        self.description = data.description
        if data.scene_type == SceneType.DUNGEON:
            assert data.map_file is not None
            self.controller = DungeonController(data.map_file)

    def start(self, player: Player):
        self.controller.set_player(player)

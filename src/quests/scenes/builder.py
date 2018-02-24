from enum import Enum
from typing import Dict, Any, List, Callable

from quests.scenes.decisions import DecisionScene
from quests.scenes.dungeons import DungeonScene
from quests.scenes.interface import Scene
from quests.scenes.skill_checks import SkillCheckScene
from quests.scenes.transitions import TransitionScene


class SceneType(Enum):
    DUNGEON = 'dungeon'
    DECISION = 'decision'
    TRANSITION = 'transition'
    SKILL_CHECK = 'skill check'

    def arg_labels(self) -> List[str]:
        return _arg_labels[self]

    def scene_constructor(self) -> Callable:
        return _scene_map[self]


_arg_labels = {SceneType.DUNGEON: ['map file', 'resolutions'],
               SceneType.DECISION: ['description', 'choices'],
               SceneType.TRANSITION: ['description'],
               SceneType.SKILL_CHECK: ['success', 'failure', 'difficulty']}
_scene_map = {SceneType.DUNGEON: DungeonScene,
              SceneType.DECISION: DecisionScene,
              SceneType.TRANSITION: TransitionScene,
              SceneType.SKILL_CHECK: SkillCheckScene}


def make_scene(scene_data: Dict[str, Any]) -> Scene:
    scene_type = SceneType(scene_data['type'])
    args = [scene_data[arg_label] for arg_label in scene_type.arg_labels()]
    constructor = scene_type.scene_constructor()
    return constructor(*args)

from enum import Enum
from typing import Dict, Any, List, Callable

from quests.scenes.decisions import DecisionScene
from quests.scenes.dungeons import DungeonScene
from quests.scenes.turnbased import TurnBasedScene
from quests.scenes.interface import Scene
from quests.scenes.skill_checks import SkillCheckScene
from quests.scenes.transitions import TransitionScene


class SceneType(Enum):
    DUNGEON = 'dungeon'
    DECISION = 'decision'
    TRANSITION = 'transition'
    SKILL_CHECK = 'skill check'
    TURNBASED = 'turnbased'

    @property
    def arg_labels(self) -> List[str]:
        return _arg_labels[self]

    def scene_constructor(self) -> Callable:
        return _scene_map[self]


_arg_labels = {SceneType.DUNGEON: ['map file', 'resolutions'],
               SceneType.TURNBASED: ['map file', 'resolutions'],
               SceneType.DECISION: ['description', 'choices'],
               SceneType.TRANSITION: ['description', 'gained item label'],
               SceneType.SKILL_CHECK: ['success', 'failure', 'difficulty']}
_scene_map = {SceneType.DUNGEON: DungeonScene,
              SceneType.TURNBASED: TurnBasedScene,
              SceneType.DECISION: DecisionScene,
              SceneType.TRANSITION: TransitionScene,
              SceneType.SKILL_CHECK: SkillCheckScene}


def make_scene(scene_data: Dict[str, Any]) -> Scene:
    scene_type = SceneType(scene_data['type'])
    args = [scene_data[arg_label] for arg_label in scene_type.arg_labels]
    constructor = scene_type.scene_constructor()
    return constructor(*args)


def next_scene_labels(scene_data: Dict[str, Any]) -> List[str]:
    scene_labels = []
    scene_type = SceneType(scene_data['type'])
    if scene_type == SceneType.DECISION:
        for index, choice in enumerate(scene_data['choices']):
            assert len(choice.values()) == 1
            choice_data = list(choice.values())[0]
            scene_labels.append(choice_data['next scene'])
    elif scene_type == SceneType.TRANSITION:
        scene_labels.append(scene_data['next scene'])
    elif scene_type == SceneType.SKILL_CHECK:
        scene_labels.append(scene_data['success']['next scene'])
        scene_labels.append(scene_data['failure']['next scene'])
    else:
        assert scene_type in (SceneType.DUNGEON, SceneType.TURNBASED)
        for index, resolution in enumerate(scene_data['resolutions']):
            assert len(resolution.values()) == 1
            res_data = list(resolution.values())[0]
            scene_labels.append(res_data['next scene'])

    return scene_labels

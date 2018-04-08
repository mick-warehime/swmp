from enum import Enum
from typing import Dict, Any, List, Callable, Tuple

from editor.util import DataType
from quests.scenes.decisions import DecisionScene
from quests.scenes.dungeons import DungeonScene
from quests.scenes.interface import Scene
from quests.scenes.skill_checks import SkillCheckScene
from quests.scenes.transitions import TransitionScene
from quests.scenes.turnbased import TurnBasedScene


class SceneType(Enum):
    DUNGEON = 'dungeon'
    DECISION = 'decision'
    TRANSITION = 'transition'
    SKILL_CHECK = 'skill check'
    TURNBASED = 'turnbased'

    @property
    def arg_labels(self) -> Tuple[str, ...]:
        return _arg_labels[self]

    def scene_constructor(self) -> Callable:
        return _scene_map[self]

        # def field_type(self, arg: str) -> DataType:
        #     if arg not in self.arg_labels + ('type',):
        #         raise KeyError(
        #             'Unrecognized field {} for SceneType {}'.format(arg, self))
        #     return scene_field_type[arg]


_arg_labels = {SceneType.DUNGEON: ('map file', 'resolutions'),
               SceneType.TURNBASED: ('map file', 'resolutions'),
               SceneType.DECISION: ('description', 'choices'),
               SceneType.TRANSITION: ('description', 'gained item label'),
               SceneType.SKILL_CHECK: ('success', 'failure', 'difficulty')}
_scene_map = {SceneType.DUNGEON: DungeonScene,
              SceneType.TURNBASED: TurnBasedScene,
              SceneType.DECISION: DecisionScene,
              SceneType.TRANSITION: TransitionScene,
              SceneType.SKILL_CHECK: SkillCheckScene}

_scene_field_type = {
    'type': DataType.FIXED,
    'map file': DataType.SHORT_TEXT,
    'resolutions': DataType.NESTED,
    'description': DataType.LONG_TEXT,
    'success': DataType.NESTED,
    'failure': DataType.NESTED,
    'gained item label': DataType.SHORT_TEXT,
    'choices': DataType.NESTED,
    'difficulty': DataType.DIFFICULTY
}


def scene_field_type(arg: str) -> DataType:
    if arg not in _scene_field_type:
        raise KeyError('Unrecognized field label {}.'.format(arg))
    return _scene_field_type[arg]


def make_scene(scene_data: Dict[str, Any]) -> Scene:
    scene_type = SceneType(scene_data['type'])
    args = [scene_data[arg_label] for arg_label in scene_type.arg_labels]
    constructor = scene_type.scene_constructor()
    return constructor(*args)


def next_scene_labels(scene_data: Dict[str, Any]) -> List[str]:
    next_scene_fun = _next_scenes_fun_from_type[SceneType(scene_data['type'])]
    return next_scene_fun(scene_data)


def _turnbased_next_scenes(scene_data):
    scene_labels = []
    for index, resolution in enumerate(scene_data['resolutions']):
        assert len(resolution.values()) == 1
        res_data = list(resolution.values())[0]
        scene_labels.append(res_data['next scene'])
    return scene_labels


def _skill_check_next_scenes(scene_data):
    scene_labels = [scene_data['success']['next scene'],
                    scene_data['failure']['next scene']]
    return scene_labels


def _transition_next_scenes(scene_data):
    return [scene_data['next scene']]


def _decision_next_scenes(scene_data):
    scene_labels = []
    for index, choice in enumerate(scene_data['choices']):
        assert len(choice.values()) == 1
        choice_data = list(choice.values())[0]
        scene_labels.append(choice_data['next scene'])
    return scene_labels


_next_scenes_fun_from_type = {SceneType.DECISION: _decision_next_scenes,
                              SceneType.TRANSITION: _transition_next_scenes,
                              SceneType.SKILL_CHECK: _skill_check_next_scenes,
                              SceneType.TURNBASED: _turnbased_next_scenes,
                              SceneType.DUNGEON: _turnbased_next_scenes}

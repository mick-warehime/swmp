from typing import Dict, Any
import yaml
from enum import Enum
from quests.quest import Dungeon, Decision


class SceneData(Enum):
    TYPE = 'type'
    OPTIONS = 'options'
    MAP = 'map'
    SKILL = 'skill'
    DESCRIPTION = 'description'
    NEXT = 'next'
    PASS = 'pass'
    FAIL = 'fail'
    NONE = 'none'
    ROOT = 'root'


class SceneType(Enum):
    DUNGEON = 'dungeon'
    DECISION = 'decision'


# TODO - move this to its own module imported by player and quest loader
class Skills(Enum):
    SNEAK = 'sneak'


def load_quest_from_dict(quest: Dict) -> Any:
    loader = Loader(quest)
    return loader.build_quest()


def load_quest_from_file(questfile_path: str) -> Any:
    with open(questfile_path, 'r') as stream:
        quest_data = yaml.load(stream)
        return load_quest_from_dict(quest_data)


class Loader(object):
    def __init__(self, quest: Dict) -> None:
        self.quest = quest
        self.is_valid = False
        self.validate()

    def validate(self) -> None:
        has_root = False
        for scene_name in self.quest:
            scene = self.quest[scene_name]
            self.validate_scene(scene)

            if self.is_root(scene):
                if has_root:
                    raise ValueError('quest has two roots!')
                has_root = True

        if not has_root:
            raise ValueError('quest has no root!')

    def validate_scene(self, scene: Dict) -> None:
        scene_type = self.get_type(scene)

        if SceneData.DESCRIPTION.value not in scene:
            raise ValueError('"%s" scene missing description', scene)

        if scene_type == SceneType.DECISION:
            self.validate_decision_scene(scene)
        elif scene_type == SceneType.DUNGEON:
            self.validate_dungeon_scene(scene)
        else:
            msg = 'Unexpected scene type "%s"' % scene_type
            raise ValueError(msg)

        self.is_valid = True

    def validate_decision_scene(self, scene: Dict) -> None:
        if SceneData.OPTIONS.value not in scene:
            raise ValueError('"%s" scene missing options' % scene)

        options = self.get_options(scene)
        for option in options:
            result = options[option]

            pass_scene = self.get_pass(result)
            fail_scene = self.get_fail(result)

            for scene_name in [pass_scene, fail_scene]:
                # ensure the resulting scene is in the quest
                if scene_name not in self.quest:
                    raise ValueError('scene "%s" not in quest' % scene)

    def validate_dungeon_scene(self, scene: Dict) -> None:
        if SceneData.MAP.value not in scene:
            raise ValueError('"%s" scene missing map name' % scene)
        if SceneData.NEXT.value not in scene:
            raise ValueError('"%s" scene missing next scene' % scene)

        next_scene = self.get_next(scene)

        # terminal dungeon
        if next_scene.lower() == SceneData.NONE.value:
            return

        if next_scene not in self.quest:
            raise ValueError('next scene "%s" not in quest' % next_scene)

    def get_type(self, scene: Dict) -> SceneType:
        if SceneData.TYPE.value not in scene:
            raise ValueError('"%s" scene missing type value' % scene)
        type_val = scene[SceneData.TYPE.value]
        return SceneType(type_val)

    def get_map(self, scene: Dict) -> str:
        if SceneData.MAP.value not in scene:
            raise ValueError('"%s" scene missing map value' % scene)
        return scene[SceneData.MAP.value]

    def get_description(self, scene: Dict) -> str:
        if SceneData.DESCRIPTION.value not in scene:
            raise ValueError('"%s" scene missing description value' % scene)
        return scene[SceneData.DESCRIPTION.value]

    def get_options(self, scene: Dict) -> dict:
        if SceneData.OPTIONS.value not in scene:
            raise ValueError('"%s" scene missing options value' % scene)
        return scene[SceneData.OPTIONS.value]

    def get_next(self, scene: Dict) -> str:
        if SceneData.NEXT.value not in scene:
            raise ValueError('"%s" scene missing next value' % scene)
        return scene[SceneData.NEXT.value]

    def get_pass(self, option: Dict) -> str:
        if SceneData.PASS.value not in option:
            raise ValueError('"%s" option missing pass value' % option)
        return option[SceneData.PASS.value]

    def get_fail(self, option: Dict) -> str:
        if SceneData.FAIL.value not in option:
            raise ValueError('"%s" option missing fail value' % option)
        return option[SceneData.FAIL.value]

    def is_root(self, scene: Dict) -> bool:
        return SceneData.ROOT.value in scene

    def root_scene(self) -> str:
        for scene_name in self.quest:
            scene = self.quest[scene_name]
            if self.is_root(scene):
                return scene_name
        raise ValueError('no root scene')

    def build_quest(self) -> Any:

        # TODO - build quest graph given the dict in self.quest,
        # first need to ensure decisions can handle options with random result

        # dungeons = self.build_dungeons()
        # decisions = self.build_decisions()
        #
        # root_scene_name = self.root_scene()
        # print(root_scene_name)
        # if root_scene_name in decisions:
        #     root_scene = decisions[root_scene_name]
        # else:
        #     root_scene = dungeons[root_scene_name]
        #
        # g = nx.DiGraph()
        pass

    def build_dungeons(self) -> Dict:
        dungeons: Dict[str, Dungeon] = {}
        for scene_name in self.quest:
            scene = self.quest[scene_name]
            scene_type = self.get_type(scene)
            if scene_type != SceneType.DUNGEON:
                continue
            description = self.get_description(scene)
            map_name = self.get_map(scene)
            dungeons[scene_name] = Dungeon(description, map_name)
        return dungeons

    def build_decisions(self) -> Dict:
        decisions: Dict[str, Dungeon] = {}
        for scene_name in self.quest:
            scene = self.quest[scene_name]
            scene_type = self.get_type(scene)
            if scene_type != SceneType.DECISION:
                continue
            description = self.get_description(scene)
            skills = self.get_options(scene)

            # TODO - decisions should handle a dict of options
            # maps skill : { pass: pass.tmx, fail: fail:fail.tmx}
            options = []
            for skill_name in skills:
                result = skills[skill_name]
                options.append(result['text'])
            decisions[scene_name] = Decision(description, options)

        return decisions


load_quest_from_file('sample_quest.yml')

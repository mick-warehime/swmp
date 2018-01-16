import unittest
from typing import Dict, Any
from quests.loader import load_quest_from_dict


def decision_description() -> Dict[str, Any]:
    return {'description': 'Sample Scene Description',
            'type': 'decision',
            'root': 'True',
            'options': {'sneak': {'pass': 'pass_scene', 'fail': 'fail_scene'}}}


def dungeon_description() -> Dict[str, Any]:
    return {'description': 'Sample Scene Description',
            'type': 'dungeon',
            'map': 'princess_dvir',
            'next': 'None',
            'root': 'True'}


def default_dungeon() -> Dict[str, Any]:
    return {'scene_name': dungeon_description()}


def default_decision(description: Any) -> Dict[str, Any]:
    decision = {'scene_name': description}
    dungeon = dungeon_description()
    del dungeon['root']
    decision['pass_scene'] = dungeon
    decision['fail_scene'] = dungeon
    return decision


class LoadQuestTest(unittest.TestCase):
    def test_load_dungeon(self) -> None:
        dungeon = default_dungeon()
        load_quest_from_dict(dungeon)

    def test_load_decision(self) -> None:
        decision = default_decision(decision_description())
        load_quest_from_dict(decision)

    def test_dungeon_validation(self) -> None:
        description = dungeon_description()

        for description_key in description:
            description_copy = description.copy()
            del description_copy[description_key]
            dungeon = {'scene_name': description_copy}

            self.assertRaises(ValueError, load_quest_from_dict, dungeon)

    def test_decision_validation(self) -> None:
        description = decision_description()

        for description_key in description:
            description_copy = description.copy()
            del description_copy[description_key]
            decision = default_decision(description_copy)

            self.assertRaises(ValueError, load_quest_from_dict, decision)

    def validate_two_roots(self) -> None:
        decision = {'scene_name': decision_description()}
        dungeon = dungeon_description()
        decision['pass_scene'] = dungeon
        decision['fail_scene'] = dungeon
        self.assertRaises(ValueError, load_quest_from_dict, decision)


from typing import Dict, Any
import yaml

TYPE = 'type'
OPTION = 'option'
MAP = 'map'
SKILL = 'skill'

# TODO - move this to its own module imported by player and quest loader
VALID_SKILLS = ['sneak']


def load_quest_from_dict(quest_dict: Dict) -> Any:
    pass


def load_quest_from_file(questfile_path: str) -> Any:
    pass


def is_valid_scene(scene_dict: Dict) -> bool:
    return True


quest_data = 'first_quest.yml'
with open(quest_data, 'r') as stream:
    data = yaml.load(stream)
    for scene in data:
        print(scene)

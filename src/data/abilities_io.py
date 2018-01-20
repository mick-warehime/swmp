from typing import Set, Dict, Union

import yaml

from os import path

_ABILITIES_FILE = path.dirname(__file__) + '/abilities.yml'

with open(_ABILITIES_FILE, 'r') as stream:
    _abilities_data = yaml.load(stream)


def load_ability_data_kwargs(name: str) -> Dict[str, Union[int, float, str]]:
    for ability_type, ability_kwargs in _abilities_data.items():
        if name in ability_kwargs:
            return ability_kwargs[name]
    raise KeyError('Ability name %s not recognized' % (name,))


def sound_filenames() -> Set[str]:
    filenames = set()
    for ability_types in _abilities_data.values():
        for ability_data in ability_types.values():
            sound_file = ability_data['sound_on_use']
            if sound_file is not None:
                filenames.add(sound_file)
    return filenames

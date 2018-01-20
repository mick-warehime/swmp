import yaml

from abilities import AbilityData

from os import path

_ABILITIES_FILE = path.dirname(__file__) + '/abilities.yml'

with open(_ABILITIES_FILE, 'r') as stream:
    _abilities_data = yaml.load(stream)


def load_ability_data(name: str) -> AbilityData:
    for ability_type, ability_kwargs in _abilities_data.items():
        if name in ability_kwargs:
            return AbilityData(**ability_kwargs[name])
    raise KeyError('Ability name %s not recognized' % (name,))

import yaml

from abilities import AbilityData

from src import __path__ as _src_path  # type: ignore

_src_path = _src_path[0]

_ABILITIES_FILE = _src_path + '/data/abilities.yml'


# TODO(dvirk): The MuzzleFlash must be added back in later.

# TODO(dvirk): Currently the file is read every time load... is
#  called. This is unnecessary and should be done once.
def load_ability_data(name: str) -> AbilityData:
    with open(_ABILITIES_FILE, 'r') as stream:
        all_data = yaml.load(stream)

        for ability_type, ability_kwargs in all_data.items():
            if name in ability_kwargs:
                return AbilityData(**ability_kwargs[name])
        raise KeyError('Ability name %s not recognized' % (name,))

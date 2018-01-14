from typing import Any

import yaml

from abilities import AbilityData, ProjectileAbilityData, \
    RegenerationAbilityData
from projectiles import ProjectileData

from src import __path__ as _src_path  # type: ignore

_src_path = _src_path[0]

_PROJECTILE_FILE = _src_path + '/data/projectiles.yml'
_ABILITIES_FILE = _src_path + '/data/abilities.yml'


def print_rock_err_msg(*args: Any) -> None:
    print('Missing RockObject')


# TODO(dvirk): Currently the file is read every time load_projectile_data is
#  called. This is unnecessary and should be done once.
def load_projectile_data(name: str) -> ProjectileData:
    with open(_PROJECTILE_FILE, 'r') as stream:
        data = yaml.load(stream)
        if name not in data:
            raise KeyError('Unrecognized projectile name: %s' % (name,))
        kwargs = data[name]
        if 'drops_on_kill' in kwargs:
            assert kwargs['drops_on_kill'] == 'RockObject'
            kwargs['drops_on_kill'] = print_rock_err_msg
        return ProjectileData(**kwargs)


_ability_constructors = {'projectile': ProjectileAbilityData,
                         'regeneration': RegenerationAbilityData}


def load_ability_data(name: str) -> AbilityData:
    with open(_ABILITIES_FILE, 'r') as stream:
        all_data = yaml.load(stream)

        for ability_type, ability_kwargs in all_data.items():
            if name in ability_kwargs:
                constructor = _ability_constructors[ability_type]
                return constructor(**ability_kwargs[name])
        raise KeyError('Ability name %s not recognized' % (name,))

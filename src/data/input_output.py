from typing import Any

import yaml

from projectiles import ProjectileData

from src import __path__ as _src_path  # type: ignore

_src_path = _src_path[0]

PROJECTILE_FILE = _src_path + "/data/projectiles.yml"


def print_rock_err_msg(*args: Any) -> None:
    print('Missing RockObject')


def load_projectile_data(name: str) -> ProjectileData:
    with open(PROJECTILE_FILE, 'r') as stream:
        try:
            data = yaml.load(stream)
            kwargs = data[name]
            if 'drops_on_kill' in kwargs:
                assert kwargs['drops_on_kill'] == 'RockObject'
                kwargs['drops_on_kill'] = print_rock_err_msg
            return ProjectileData(**kwargs)
        except yaml.YAMLError as exc:
            print(exc)

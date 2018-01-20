from typing import Any

import yaml

from projectiles import ProjectileData

from os import path

_PROJECTILE_FILE = path.dirname(__file__) + '/projectiles.yml'

with open(_PROJECTILE_FILE, 'r') as stream:
    _projectile_data = yaml.load(stream)


def load_projectile_data(name: str) -> ProjectileData:
    if name not in _projectile_data:
        raise KeyError('Unrecognized projectile name: %s' % (name,))
    kwargs = _projectile_data[name]
    return ProjectileData(**kwargs)

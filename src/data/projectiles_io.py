from typing import Set, Union, Dict

import yaml

from os import path

_PROJECTILE_FILE = path.dirname(__file__) + '/projectiles.yml'

with open(_PROJECTILE_FILE, 'r') as stream:
    _projectile_data = yaml.load(stream)


def load_projectile_data_kwargs(name: str) -> Dict[
    str, Union[int, float, str]]:
    if name not in _projectile_data:
        raise KeyError('Unrecognized projectile name: %s' % (name,))
    return _projectile_data[name]


def image_filenames() -> Set[str]:
    filenames = set()
    for projectile in _projectile_data.values():
        filenames.add(projectile['image_file'])
    return filenames

from typing import Set, Union, Dict

import yaml

from os import path

_MODS_FILE = path.dirname(__file__) + '/mods.yml'

with open(_MODS_FILE, 'r') as stream:
    _mods_data = yaml.load(stream)


def load_mod_data_kwargs(name: str) -> Dict[str, Union[str, int, float, bool]]:
    if name in _mods_data:
        return _mods_data[name]
    raise KeyError('Mod name %s not recognized' % (name,))


def image_filenames() -> Set[str]:
    filenames = set()
    for mod_data_dict in _mods_data.values():
        if 'equipped_image_file' not in mod_data_dict:
            continue  # Skip default specifications
        image_file = mod_data_dict['equipped_image_file']
        if image_file:
            filenames.add(image_file)
        image_file = mod_data_dict['backpack_image_file']
        if image_file:
            filenames.add(image_file)

    return filenames

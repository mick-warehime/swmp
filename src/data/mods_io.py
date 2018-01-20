import yaml

from os import path

from mods import ModData

_MODS_FILE = path.dirname(__file__) + '/mods.yml'

with open(_MODS_FILE, 'r') as stream:
    _mods_data = yaml.load(stream)


def load_mod_data(name: str) -> ModData:
    if name in _mods_data:
        return ModData(**_mods_data[name])
    raise KeyError('Mod name %s not recognized' % (name,))

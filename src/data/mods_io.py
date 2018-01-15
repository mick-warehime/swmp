import yaml

from os import path

from mods import ModData

_MODS_FILE = path.dirname(__file__) + '/mods.yml'


# TODO(dvirk): Currently the file is read every time load... is
#  called. This is unnecessary and should be done once.
def load_mod_data(name: str) -> ModData:
    with open(_MODS_FILE, 'r') as stream:
        all_data = yaml.load(stream)

        if name in all_data:
            return ModData(**all_data[name])
        raise KeyError('Mod name %s not recognized' % (name,))

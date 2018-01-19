import yaml

from os import path

from items_module import ItemData

_ITEMS_FILE = path.dirname(__file__) + '/items.yml'


# TODO(dvirk): Currently the file is read every time load... is
#  called. This is unnecessary and should be done once.
def load_item_data(name: str) -> ItemData:
    with open(_ITEMS_FILE, 'r') as stream:
        all_data = yaml.load(stream)

        if name in all_data:
            return ItemData(**all_data[name])
        raise KeyError('Item name %s not recognized' % (name,))

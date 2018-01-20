from os import path

import yaml

from items import ItemData

_ITEMS_FILE = path.dirname(__file__) + '/items.yml'

with open(_ITEMS_FILE, 'r') as stream:
    _items_data = yaml.load(stream)


def load_item_data(name: str) -> ItemData:
    if name in _items_data:
        return ItemData(**_items_data[name])
    raise KeyError('Item name %s not recognized' % (name,))

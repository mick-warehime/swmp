from typing import Union

import pygame as pg

from data.items_io import load_item_data
from items import ItemFromData
from tilemap import ObjectType


class ItemManager(object):
    @staticmethod
    def item(pos: pg.math.Vector2,
             label: Union[ObjectType, str]) -> ItemFromData:
        # TODO(dvirk): This is a bit kludgy. We need to decide whether we
        # still want to use the ObjectType class for construction.
        if isinstance(label, ObjectType):
            label = label.value  # type: ignore

        item_data = load_item_data(label)
        return ItemFromData(item_data, pos)
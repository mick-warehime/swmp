import pygame as pg

from data.items_io import load_item_data
from items.items_module import ItemObject, ItemFromData
from tilemap import ObjectType


class ItemManager(object):
    @staticmethod
    def item(pos: pg.math.Vector2, label: ObjectType) -> ItemObject:
        item_data = load_item_data(label.value)
        return ItemFromData(item_data, pos)
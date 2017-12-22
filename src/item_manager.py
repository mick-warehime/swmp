from settings import ItemType
import pygame as pg
from mod import HealthPackObject, PistolObject, ShotgunObject, ItemObject

item_contructors = {ItemType.healthpack: HealthPackObject,
                    ItemType.shotgun: ShotgunObject,
                    ItemType.pistol: PistolObject}


class ItemManager(object):
    @staticmethod
    def item(pos: pg.math.Vector2, item_type: ItemType) -> ItemObject:
        return item_contructors[item_type](pos)

    @staticmethod
    def is_item(label: str) -> bool:
        try:
            ItemManager.get_item_type(label)
            return True
        except ValueError:
            return False

    @staticmethod
    def get_item_type(label: str) -> ItemType:
        if label == 'pistol':
            return ItemType.pistol
        if label == 'shotgun':
            return ItemType.shotgun
        if label == 'healthpack':
            return ItemType.healthpack

        raise ValueError('unknown item type \'%s\'' % label)

import pygame as pg

from data.items_io import load_item_data
from items.bullet_weapons import PistolObject, ShotgunObject
from items.laser_weapons import LaserGun
from items.rocks import RockObject
from items.utility_items import HealthPackObject, Battery
from items_module import ItemObject, ItemFromData
from tilemap import ObjectType

item_contructors = {ObjectType.HEALTHPACK: HealthPackObject,
                    ObjectType.SHOTGUN: ShotgunObject,
                    ObjectType.PISTOL: PistolObject,
                    ObjectType.ROCK: RockObject,
                    ObjectType.LASER_GUN: LaserGun,
                    ObjectType.BATTERY: Battery}


class ItemManager(object):
    @staticmethod
    def item(pos: pg.math.Vector2, label: ObjectType) -> ItemObject:

        item_data = load_item_data(label.value)
        return ItemFromData(item_data, pos)

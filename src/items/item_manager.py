import pygame as pg

from items.bullet_weapons import PistolObject, ShotgunObject
from items.laser_weapons import LaserGun
from items.rocks import RockObject
from items.utility_items import HealthPackObject, Battery
from items_module import ItemObject
from tilemap import ObjectType

item_contructors = {ObjectType.HEALTHPACK: HealthPackObject,
                    ObjectType.SHOTGUN: ShotgunObject,
                    ObjectType.PISTOL: PistolObject,
                    ObjectType.ROCK: RockObject,
                    ObjectType.LASER_GUN: LaserGun,
                    ObjectType.BATTERY: Battery}


class ItemManager(object):
    @staticmethod
    def item(pos: pg.math.Vector2, label: str) -> ItemObject:
        if label not in item_contructors:
            error_msg = 'Item label %s not recognized.'
            raise ValueError(error_msg % (label,))

        return item_contructors[label](pos)

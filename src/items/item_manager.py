import pygame as pg

from items.laser_weapons import LaserGun
from mods import ItemObject
from items.utility_items import HealthPackObject
from items.bullet_weapons import PistolObject, ShotgunObject
from items.rocks import RockObject
from tilemap import ObjectType

item_contructors = {ObjectType.HEALTHPACK: HealthPackObject,
                    ObjectType.SHOTGUN: ShotgunObject,
                    ObjectType.PISTOL: PistolObject,
                    ObjectType.ROCK: RockObject,
                    ObjectType.LASER_GUN: LaserGun}


class ItemManager(object):
    @staticmethod
    def item(pos: pg.math.Vector2, label: str) -> ItemObject:
        if label not in item_contructors:
            error_msg = 'Item label %s not recognized.'
            raise ValueError(error_msg % (label,))

        return item_contructors[label](pos)

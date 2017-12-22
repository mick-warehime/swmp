import pygame as pg
from mod import HealthPackObject, PistolObject, ShotgunObject, ItemObject
from tilemap import ObjectType

item_contructors = {ObjectType.HEALTHPACK: HealthPackObject,
                    ObjectType.SHOTGUN: ShotgunObject,
                    ObjectType.PISTOL: PistolObject}


class ItemManager(object):
    @staticmethod
    def item(pos: pg.math.Vector2, label: str) -> ItemObject:
        if label not in item_contructors:
            error_msg = 'Item label %s not recognized.'
            raise ValueError(error_msg % (label,))

        return item_contructors[label](pos)

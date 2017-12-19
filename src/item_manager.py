import settings
import pygame as pg
from model import Groups, Item
from mod import ShotgunMod, HealthPack, PistolObject

item_contructors = {settings.HEALTHPACK_ITEM: HealthPack,
                    settings.SHOTGUN_MOD: ShotgunMod,
                    settings.PISTOL_MOD: PistolObject}


class ItemManager(object):
    @staticmethod
    def item(groups: Groups, pos: pg.math.Vector2,
             label: str) -> Item:
        if label not in item_contructors:
            error_msg = 'Item label %s not recognized.'
            raise ValueError(error_msg % (label,))

        ctr = item_contructors[label]
        if label == settings.PISTOL_MOD:
            return ctr(pos)
        return ctr(groups, pos)

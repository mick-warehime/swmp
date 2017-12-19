import settings
import pygame as pg
from model import Groups, Item
from mod import ShotgunMod, PistolMod, HealthPack

item_contructors = {settings.HEALTHPACK_ITEM: HealthPack,
                    settings.SHOTGUN_MOD: ShotgunMod,
                    settings.PISTOL_MOD: PistolMod}


class ItemManager(object):
    @staticmethod
    def item(groups: Groups, pos: pg.math.Vector2,
             label: str) -> Item:
        if label not in item_contructors:
            error_msg = 'Item label %s not recognized.'
            raise ValueError(error_msg % (label,))

        ctr = item_contructors[label]
        return ctr(groups, pos)

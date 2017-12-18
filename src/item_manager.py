import settings
import pygame as pg
from model import Groups, Item, HealthPack
from mod import ShotgunMod, PistolMod

class ItemManager(object):

    @staticmethod
    def item(groups: Groups, pos: pg.math.Vector2,
                 label: str) -> Item:
        if label == settings.HEALTHPACK_ITEM:
            return HealthPack(groups, pos, label)
        if label == settings.SHOTGUN_MOD:
            return ShotgunMod(groups, pos, label)
        if label == settings.PISTOL_MOD:
            return PistolMod(groups, pos, label)

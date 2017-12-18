from enum import Enum
import pygame as pg
import images
import weapon


class ModID(Enum):
    PISTOL = 0
    SHOTGUN = 1


class ModLocation(Enum):
    __order__ = 'ARMS LEGS CHEST HEAD'
    ARMS = 0
    LEGS = 1
    CHEST = 2
    HEAD = 3


class Mod(object):
    def __init__(self,
                 sid: ModID,
                 loc: ModLocation,
                 image: pg.Surface) -> None:

        self.sid = sid
        self.loc = loc
        self.image = image


class ShotgunMod(Mod):
    def __init__(self) -> None:
        sid = ModID.SHOTGUN
        loc = ModLocation.ARMS
        img = images.get_image(images.SHOTGUN_SKILL)
        super(ShotgunMod, self).__init__(sid=sid,
                                         loc=loc,
                                         image=img)

        self.weapon = weapon.Weapon()


class PistolMod(Mod):
    def __init__(self) -> None:
        sid = ModID.PISTOL
        loc = ModLocation.ARMS
        img = images.get_image(images.PISTOL_SKILL)
        super(PistolMod, self).__init__(sid=sid,
                                        loc=loc,
                                        image=img)

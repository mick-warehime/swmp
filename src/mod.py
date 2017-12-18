from enum import Enum
import pygame as pg
import images
import weapon


class ModID(Enum):
    PISTOL = 0
    SHOTGUN = 1


class Mod(object):
    def __init__(self,
                 sid: ModID,
                 image: pg.Surface) -> None:
        self.sid = sid
        self.image = image


class ShotgunMod(Mod):
    def __init__(self) -> None:
        sid = ModID.SHOTGUN
        img = images.get_image(images.SHOTGUN_SKILL)
        super(ShotgunMod, self).__init__(sid=sid, image=img)

        self.weapon = weapon.Weapon()


class PistolMod(Mod):
    def __init__(self) -> None:
        sid = ModID.PISTOL
        img = images.get_image(images.PISTOL_SKILL)
        super(PistolMod, self).__init__(sid=sid, image=img)

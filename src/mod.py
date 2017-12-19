from enum import Enum
import pygame as pg
import images
from typing import Any
import model
import settings
import sounds
from model import Item, Groups


class ModID(Enum):
    PISTOL = 0
    SHOTGUN = 1


class ModLocation(Enum):
    __order__ = 'ARMS LEGS CHEST HEAD'
    ARMS = 0
    LEGS = 1
    CHEST = 2
    HEAD = 3


class Mod(model.Item):
    def __init__(self,
                 sid: ModID,
                 loc: ModLocation,
                 image: pg.Surface,
                 groups: model.Groups,
                 pos: pg.math.Vector2,
                 label: str) -> None:
        super(Mod, self).__init__(groups, pos, label)
        self.sid = sid
        self.loc = loc
        self.mod_image = image

    '''this will equip that mod at the proper location'''

    def use(self, player: Any) -> bool:
        old_mod = None
        if self.loc in player.active_mods:
            old_mod = player.active_mods[self.loc]
        player.active_mods[self.loc] = self

        if self in player.backpack:
            player.backpack.remove(self)

        if old_mod is not None:
            player.backpack.append(old_mod)

        player.set_weapon(self.label)

        return True


class ShotgunMod(Mod):
    def __init__(self, groups: model.Groups, pos: pg.math.Vector2) -> None:
        sid = ModID.SHOTGUN
        loc = ModLocation.ARMS
        img = images.get_image(images.SHOTGUN_MOD)
        label = settings.SHOTGUN_MOD
        super(ShotgunMod, self).__init__(sid=sid,
                                         loc=loc,
                                         image=img,
                                         groups=groups,
                                         pos=pos,
                                         label=label)


class PistolMod(Mod):
    def __init__(self, groups: model.Groups, pos: pg.math.Vector2) -> None:
        sid = ModID.PISTOL
        loc = ModLocation.ARMS
        img = images.get_image(images.PISTOL_MOD)
        label = settings.PISTOL_MOD
        super(PistolMod, self).__init__(sid=sid,
                                        loc=loc,
                                        image=img,
                                        groups=groups,
                                        pos=pos,
                                        label=label)


class HealthPack(Item):
    def __init__(self, groups: Groups, pos: pg.math.Vector2) -> None:
        label = settings.HEALTHPACK_ITEM
        super(HealthPack, self).__init__(groups, pos, label)

    def use(self, player: Any) -> bool:
        if player.health < settings.PLAYER_HEALTH:
            sounds.play(sounds.HEALTH_UP)
            player.increment_health(settings.HEALTH_PACK_AMOUNT)
            player.backpack.remove(self)
            self.kill()
            return True
        return False

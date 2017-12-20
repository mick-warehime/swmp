from enum import Enum
import pygame as pg
import pytweening as tween
from pygame.math import Vector2

import images
from typing import Any
import settings
import sounds
from model import DynamicObject


class ModID(Enum):
    PISTOL = 0
    SHOTGUN = 1
    HEALTHPACK = 2


class ModLocation(Enum):
    __order__ = 'ARMS LEGS CHEST HEAD BACKPACK'
    ARMS = 0
    LEGS = 1
    CHEST = 2
    HEAD = 3
    BACKPACK = 4


class Mod(object):
    def __init__(self, sid: ModID, loc: ModLocation, image: pg.Surface,
                 label: str) -> None:
        self.sid = sid
        self.loc = loc
        self.image = image
        self.label = label

    @property
    def equipable(self) -> bool:
        return self.loc != ModLocation.BACKPACK

    @property
    def expendable(self) -> bool:
        return not self.equipable

    @property
    def expended(self) -> bool:
        raise NotImplementedError

    @property
    def use(self, player: Any) -> None:
        raise NotImplementedError


class WeaponMod(Mod):
    def __init__(self, sid: ModID, image: pg.Surface,
                 label: str) -> None:
        loc = ModLocation.ARMS
        super(WeaponMod, self).__init__(sid=sid, loc=loc, image=image,
                                        label=label)

    def use(self, player: Any) -> None:
        print('Setting weapon to %s' % self.label)
        player.set_weapon(self.label)

    @property
    def expended(self) -> bool:
        return False


class ShotgunMod(WeaponMod):
    def __init__(self) -> None:
        sid = ModID.SHOTGUN
        img = images.get_image(images.SHOTGUN_MOD)
        label = settings.SHOTGUN
        super(ShotgunMod, self).__init__(sid=sid, image=img, label=label)


class PistolMod(WeaponMod):
    def __init__(self) -> None:
        sid = ModID.PISTOL
        img = images.get_image(images.PISTOL_MOD)
        label = settings.PISTOL
        super(PistolMod, self).__init__(sid=sid, image=img, label=label)


class HealthPackMod(Mod):
    def __init__(self) -> None:
        sid = ModID.HEALTHPACK
        loc = ModLocation.BACKPACK
        img = images.get_image(images.HEALTH_PACK)
        label = settings.HEALTHPACK
        self._expended = False
        super(HealthPackMod, self).__init__(sid=sid, loc=loc, image=img,
                                            label=label)

    def use(self, player: Any) -> None:
        if player.damaged:
            sounds.play(sounds.HEALTH_UP)
            player.increment_health(settings.HEALTH_PACK_AMOUNT)
            player.backpack.remove(self)
            self._expended = True

    @property
    def expended(self):
        return self._expended


class ItemObject(DynamicObject):
    """A bobbing in-game object that can be picked up."""

    def __init__(self, mod: Mod, image: pg.Surface, pos: Vector2) -> None:
        self._check_class_initialized()
        super(ItemObject, self).__init__(image.get_rect(), pos)

        my_groups = [self._groups.all_sprites, self._groups.items]
        pg.sprite.Sprite.__init__(self, my_groups)

        self.image = image
        self._mod = mod
        self._tween = tween.easeInOutSine
        self._step = 0
        self._bob_direction = 1
        self._bob_period = settings.BOB_RANGE
        self._bob_speed = settings.BOB_SPEED

    @property
    def mod(self) -> Mod:
        return self._mod

    def update(self) -> None:
        # bobbing motion
        offset = self._bob_offset()
        self.rect.centery = self.pos.y + offset * self._bob_direction
        self._step += self._bob_speed
        if self._step > self._bob_period:
            self._step = 0
            self._bob_direction *= -1

    def _bob_offset(self) -> float:
        offset = self._bob_period * (
            self._tween(self._step / self._bob_period) - 0.5)
        return offset


class PistolObject(ItemObject):
    def __init__(self, pos: Vector2) -> None:
        self._check_class_initialized()
        mod = PistolMod()

        # TODO(dkafri): image should not need to be passed to the super.init?
        if self.base_image is None:
            self._init_base_image(images.PISTOL_MOD)

        super(PistolObject, self).__init__(mod, self.base_image, pos)


class ShotgunObject(ItemObject):
    def __init__(self, pos: Vector2) -> None:
        self._check_class_initialized()
        mod = ShotgunMod()

        # TODO(dkafri): image should not need to be passed to the super.init?
        if self.base_image is None:
            self._init_base_image(images.SHOTGUN_MOD)

        super(ShotgunObject, self).__init__(mod, self.base_image, pos)


class HealthPackObject(ItemObject):
    def __init__(self, pos: Vector2) -> None:
        self._check_class_initialized()
        mod = HealthPackMod()

        # TODO(dkafri): image should not need to be passed to the super.init?
        if self.base_image is None:
            self._init_base_image(images.HEALTH_PACK)

        super(HealthPackObject, self).__init__(mod, self.base_image, pos)

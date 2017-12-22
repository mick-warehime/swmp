from enum import Enum
import pygame as pg
import pytweening as tween
from pygame.math import Vector2

import images
from typing import Any
import settings
import sounds
from model import DynamicObject

# Items
HEALTH_PACK_AMOUNT = 20
BOB_RANGE = 10
BOB_SPEED = 0.3


class ModLocation(Enum):
    __order__ = 'ARMS LEGS CHEST HEAD BACKPACK'
    ARMS = 0
    LEGS = 1
    CHEST = 2
    HEAD = 3
    BACKPACK = 4


EQUIP_LOCATIONS = tuple(
    [loc for loc in ModLocation if loc != ModLocation.BACKPACK])


class Mod(object):
    def __init__(self,
                 item_type: settings.ItemType,
                 loc: ModLocation,
                 image: pg.Surface,
                 ) -> None:
        self.item_type = item_type
        self.loc = loc
        self.image = image

    @property
    def equipable(self) -> bool:
        return self.loc != ModLocation.BACKPACK

    @property
    def expendable(self) -> bool:
        return not self.equipable

    @property
    def expended(self) -> bool:
        raise NotImplementedError

    def use(self, player: Any) -> None:
        raise NotImplementedError


class WeaponMod(Mod):
    def __init__(self,
                 item_type: settings.ItemType,
                 image: pg.Surface) -> None:
        loc = ModLocation.ARMS
        super().__init__(item_type=item_type, loc=loc, image=image)

    # TODO(dkafri): Thus functionality should be handled by the Backpack.
    def use(self, player: Any) -> None:
        player.set_weapon(self.item_type)

    @property
    def expended(self) -> bool:
        return False


class ShotgunMod(WeaponMod):
    def __init__(self) -> None:
        img = images.get_image(images.SHOTGUN_MOD)
        item_type = settings.ItemType.shotgun
        super().__init__(item_type=item_type, image=img)


class PistolMod(WeaponMod):
    def __init__(self) -> None:
        img = images.get_image(images.PISTOL_MOD)
        item_type = settings.ItemType.pistol
        super().__init__(item_type=item_type, image=img)


class HealthPackMod(Mod):
    def __init__(self) -> None:
        loc = ModLocation.BACKPACK
        img = images.get_image(images.HEALTH_PACK)
        item_type = settings.ItemType.healthpack
        self._expended = False
        super().__init__(item_type=item_type, loc=loc, image=img)

    def use(self, player: Any) -> None:
        if player.damaged:
            sounds.play(sounds.HEALTH_UP)
            player.increment_health(HEALTH_PACK_AMOUNT)
            self._expended = True

    @property
    def expended(self) -> bool:
        return self._expended


class ItemObject(DynamicObject):
    """A bobbing in-game object that can be picked up."""

    def __init__(self, mod: Mod, image: pg.Surface, pos: Vector2) -> None:
        self._check_class_initialized()
        super().__init__(image.get_rect(), pos)

        my_groups = [self._groups.all_sprites, self._groups.items]
        pg.sprite.Sprite.__init__(self, my_groups)

        self.image = image
        self._mod = mod
        self._tween = tween.easeInOutSine
        self._step = 0.0
        self._bob_direction = 1
        self._bob_period = BOB_RANGE
        self._bob_speed = BOB_SPEED

    @property
    def mod(self) -> Mod:
        return self._mod

    def update(self) -> None:
        # bobbing motion
        offset = self._bob_offset()
        self.rect.centery = self.pos.y + offset * self._bob_direction
        self._step += self._bob_speed
        if self._step > self._bob_period:
            self._step = 0.0
            self._bob_direction *= -1

    def _bob_offset(self) -> float:
        offset = self._bob_period * (
            self._tween(self._step / self._bob_period) - 0.5)
        return offset


class PistolObject(ItemObject):
    def __init__(self, pos: Vector2) -> None:
        self._check_class_initialized()
        mod = PistolMod()

        if self.base_image is None:
            self._init_base_image(images.PISTOL)

        super().__init__(mod, self.base_image, pos)


class ShotgunObject(ItemObject):
    def __init__(self, pos: Vector2) -> None:
        self._check_class_initialized()
        mod = ShotgunMod()

        if self.base_image is None:
            self._init_base_image(images.SHOTGUN)

        super().__init__(mod, self.base_image, pos)


class HealthPackObject(ItemObject):
    def __init__(self, pos: Vector2) -> None:
        self._check_class_initialized()
        mod = HealthPackMod()

        if self.base_image is None:
            self._init_base_image(images.HEALTH_PACK)

        super().__init__(mod, self.base_image, pos)

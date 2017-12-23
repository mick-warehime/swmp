from enum import Enum
import pygame as pg
import pytweening as tween
from pygame.math import Vector2

import images
from typing import Any
import sounds
from abilities import Ability, FireShotgun, FirePistol, Heal
from model import DynamicObject

# Items
from tilemap import ObjectType

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


def initialize_classes() -> None:
    PistolMod.initialize_class()
    ShotgunMod.initialize_class()
    HealthPackMod.initialize_class()


class Mod(object):
    class_initialized = True

    @property
    def equipable(self) -> bool:
        return self.loc != ModLocation.BACKPACK

    @property
    def expendable(self) -> bool:
        return not self.equipable

    @property
    def loc(self) -> ModLocation:
        raise NotImplementedError

    @property
    def expended(self) -> bool:
        raise NotImplementedError

    def ability(self) -> Ability:
        raise NotImplementedError

    def use(self, player: Any) -> None:
        raise NotImplementedError

    @property
    def equipped_image(self) -> pg.Surface:
        raise NotImplementedError

    @property
    def backpack_image(self) -> pg.Surface:
        raise NotImplementedError

    @classmethod
    def _check_class_initialized(cls) -> None:
        if not cls.class_initialized:
            raise RuntimeError('Class %s must be initialized before '
                               'instantiating an object.' % (cls,))


class ShotgunMod(Mod):
    loc = ModLocation.ARMS
    _equipped_image = None
    _backpack_image = None
    class_initialized = False

    def __init__(self) -> None:
        self._check_class_initialized()
        self._ability = FireShotgun()

    def use(self, player: Any) -> None:
        player.set_weapon(ObjectType.SHOTGUN)

    def ability(self) -> Ability:
        return self._ability

    @property
    def expended(self) -> bool:
        return False

    @classmethod
    def initialize_class(cls) -> None:
        cls._equipped_image = images.get_image(images.SHOTGUN_MOD)
        cls._backpack_image = images.get_image(images.SHOTGUN)
        cls.class_initialized = True

    @property
    def equipped_image(self) -> pg.Surface:
        return self._equipped_image

    @property
    def backpack_image(self) -> pg.Surface:
        return self._backpack_image


class PistolMod(Mod):
    loc = ModLocation.ARMS
    _equipped_image = None
    _backpack_image = None
    class_initialized = False

    def __init__(self) -> None:
        self._check_class_initialized()
        self._ability = FirePistol()

    def use(self, player: Any) -> None:
        player.set_weapon(ObjectType.PISTOL)

    def ability(self) -> Ability:
        return self._ability

    @property
    def expended(self) -> bool:
        return False

    @classmethod
    def initialize_class(cls) -> None:
        cls._equipped_image = images.get_image(images.PISTOL_MOD)
        cls._backpack_image = images.get_image(images.PISTOL)
        cls.class_initialized = True

    @property
    def equipped_image(self) -> pg.Surface:
        return self._equipped_image

    @property
    def backpack_image(self) -> pg.Surface:
        return self._backpack_image


class HealthPackMod(Mod):
    loc = ModLocation.BACKPACK
    _backpack_image = None
    class_initialized = False

    def __init__(self) -> None:
        self._check_class_initialized()
        self._expended = False
        self._ability = Heal(1, HEALTH_PACK_AMOUNT)

    def use(self, player: Any) -> None:
        if player.damaged:
            sounds.play(sounds.HEALTH_UP)
            player.increment_health(HEALTH_PACK_AMOUNT)
            self._expended = True

    def ability(self) -> Ability:
        return self._ability

    @classmethod
    def initialize_class(cls) -> None:
        cls._backpack_image = images.get_image(images.HEALTH_PACK)
        cls.class_initialized = True

    @property
    def expended(self) -> bool:
        return self._expended

    @property
    def backpack_image(self) -> pg.Surface:
        return self._backpack_image

    @property
    def equipped_image(self) -> pg.Surface:
        raise RuntimeError('Healthpack has no equipped image.')


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

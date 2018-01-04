from enum import Enum
from typing import List

import pygame as pg
import pytweening as tween
from pygame.math import Vector2

import images
from abilities import Ability, Heal
from model import DynamicObject

HEALTH_PACK_AMOUNT = 20
BOB_RANGE = 1
BOB_SPEED = 0.3
BOB_PERIOD = 10

NO_MOD_AT_LOCATION = -1


class ModLocation(Enum):
    __order__ = 'ARMS LEGS CHEST HEAD'
    ARMS = 0
    LEGS = 1
    CHEST = 2
    HEAD = 3


class Buffs(Enum):
    ARMOR = 'armor'
    DAMAGE = 'damage'
    RANGE = 'range'


class Proficiencies(Enum):
    TALKING = 'talking'
    STEALTH = 'stealth'
    ATHLETICISM = 'athleticism'


class Mod(object):
    def __init__(self, buffs: List[Buffs] = None,
                 profs: List[Proficiencies] = None) -> None:
        buffs = [] if buffs is None else buffs
        profs = [] if profs is None else profs

        self._buffs = list(buffs)
        self._profs = list(profs)

    @property
    def loc(self) -> ModLocation:
        raise NotImplementedError

    @property
    def expended(self) -> bool:
        raise NotImplementedError

    @property
    def ability(self) -> Ability:
        raise NotImplementedError

    @property
    def stackable(self) -> bool:
        raise NotImplementedError

    @property
    def equipped_image(self) -> pg.Surface:
        raise NotImplementedError

    @property
    def backpack_image(self) -> pg.Surface:
        raise NotImplementedError

    @property
    def description(self) -> str:
        raise NotImplementedError

    def __str__(self) -> str:
        output = '%s' % (self.description)
        if self._buffs or self._profs:
            output += '('
            for buff in self._buffs:
                output += '%s, ' % (buff.value,)
            for prof in self._profs:
                output += '%s, ' % (prof.value,)
            output += ')'
        return output


class HealthPackMod(Mod):
    loc = ModLocation.CHEST

    def __init__(self, buffs: List[Buffs] = None,
                 perks: List[Proficiencies] = None) -> None:
        super().__init__(buffs, perks)
        self._expended = False
        self._ability = Heal(1, HEALTH_PACK_AMOUNT)

    @property
    def ability(self) -> Ability:
        return self._ability

    @property
    def expended(self) -> bool:
        return self._ability.uses_left <= 0

    @property
    def stackable(self) -> bool:
        return True

    @property
    def backpack_image(self) -> pg.Surface:
        return images.get_image(images.HEALTH_PACK)

    @property
    def equipped_image(self) -> pg.Surface:
        return images.get_image(images.HEALTH_PACK)

    @property
    def description(self) -> str:
        return 'Healthpack'


class ItemObject(DynamicObject):
    """A bobbing in-game object that can be picked up."""

    def __init__(self, mod: Mod, pos: Vector2) -> None:
        self._check_class_initialized()
        super().__init__(pos)

        my_groups = [self._groups.all_sprites, self._groups.items]
        pg.sprite.Sprite.__init__(self, my_groups)

        self._base_rect = self.image.get_rect().copy()

        self._mod = mod
        self._tween = tween.easeInOutSine
        self._step = 0.0
        self._bob_direction = 1
        self._bob_range = BOB_RANGE
        self._bob_period = BOB_PERIOD
        self._bob_speed = BOB_SPEED

    @property
    def mod(self) -> Mod:
        return self._mod

    def update(self) -> None:
        # bobbing motion
        offset = self._bob_offset()
        self.pos.y += offset * self._bob_direction
        self._step += self._bob_speed
        if self._step > self._bob_period:
            self._step = 0.0
            self._bob_direction *= -1

    def _bob_offset(self) -> float:
        offset = self._bob_range * (
            self._tween(self._step / self._bob_period) - 0.5)
        return offset

    @property
    def rect(self) -> pg.Rect:
        self._base_rect.center = self.pos
        return self._base_rect

    @property
    def image(self) -> pg.Surface:
        raise NotImplementedError


class HealthPackObject(ItemObject):
    def __init__(self, pos: Vector2) -> None:
        self._check_class_initialized()
        mod = HealthPackMod()

        super().__init__(mod, pos)

    @property
    def image(self) -> pg.Surface:
        return images.get_image(images.HEALTH_PACK)

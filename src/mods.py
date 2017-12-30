from enum import Enum

import pygame as pg
import pytweening as tween
from pygame.math import Vector2

import images
from abilities import Ability, FireShotgun, FirePistol, Heal, SpewVomit
from model import DynamicObject
from settings import RED

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


class Mod(object):
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

    def increment_uses(self, num_uses: int) -> None:
        assert self.stackable
        assert hasattr(self.ability, 'uses_left')
        self.ability.uses_left += num_uses

    def draw_cooldown(self, image: pg.Surface) -> pg.Surface:
        if self.ability.cooldown_fraction > 1:  # No bar necessary
            return image
        image = image.copy()  # Original image should be unchanged.
        col = RED
        rect = image.get_rect()
        image_height = rect.height
        image_width = rect.width
        width = image_width * (1 - self.ability.cooldown_fraction)
        if width > 0:
            cooldown_bar = pg.Rect(0, image_height - 7, width, 7)
            pg.draw.rect(image, col, cooldown_bar)
        return image


class ShotgunMod(Mod):
    loc = ModLocation.ARMS

    def __init__(self) -> None:
        self._ability = FireShotgun()

    @property
    def ability(self) -> Ability:
        return self._ability

    @property
    def expended(self) -> bool:
        return False

    @property
    def stackable(self) -> bool:
        return False

    @property
    def equipped_image(self) -> pg.Surface:
        return images.get_image(images.SHOTGUN_MOD)

    @property
    def backpack_image(self) -> pg.Surface:
        return images.get_image(images.SHOTGUN)


class PistolMod(Mod):
    loc = ModLocation.ARMS

    def __init__(self) -> None:
        self._ability = FirePistol()

    @property
    def ability(self) -> Ability:
        return self._ability

    @property
    def expended(self) -> bool:
        return False

    @property
    def stackable(self) -> bool:
        return False

    @property
    def equipped_image(self) -> pg.Surface:
        return images.get_image(images.PISTOL_MOD)

    @property
    def backpack_image(self) -> pg.Surface:
        return images.get_image(images.PISTOL)


class VomitMod(Mod):
    loc = ModLocation.HEAD

    def __init__(self) -> None:
        self._ability = SpewVomit()

    @property
    def ability(self) -> Ability:
        return self._ability

    @property
    def expended(self) -> bool:
        return False

    @property
    def stackable(self) -> bool:
        return False

    @property
    def equipped_image(self) -> pg.Surface:
        raise RuntimeError('This is a zombie ability and should not be '
                           'visible.')

    @property
    def backpack_image(self) -> pg.Surface:
        raise RuntimeError('This is a zombie ability and should not be '
                           'visible.')


class HealthPackMod(Mod):
    loc = ModLocation.CHEST

    def __init__(self) -> None:
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


class PistolObject(ItemObject):
    def __init__(self, pos: Vector2) -> None:
        self._check_class_initialized()
        mod = PistolMod()

        super().__init__(mod, pos)

    @property
    def image(self) -> pg.Surface:
        return images.get_image(images.PISTOL)


class ShotgunObject(ItemObject):
    def __init__(self, pos: Vector2) -> None:
        self._check_class_initialized()
        mod = ShotgunMod()

        super().__init__(mod, pos)

    @property
    def image(self) -> pg.Surface:
        return images.get_image(images.SHOTGUN)


class HealthPackObject(ItemObject):
    def __init__(self, pos: Vector2) -> None:
        self._check_class_initialized()
        mod = HealthPackMod()

        super().__init__(mod, pos)

    @property
    def image(self) -> pg.Surface:
        return images.get_image(images.HEALTH_PACK)

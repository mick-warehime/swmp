from collections import namedtuple

import pygame as pg
import pytweening as tween
from pygame.math import Vector2

from data.mods_io import load_mod_data
from model import DynamicObject
from mods import Mod, BOB_RANGE, BOB_PERIOD, BOB_SPEED


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


BaseItemData = namedtuple('BaseItemData', ('mod_data', 'image_file'))


class ItemData(BaseItemData):
    def __new__(cls, mod_label: str, image_file: str) -> None:
        mod_data = load_mod_data(mod_label)

        return super().__new__(cls, mod_data, image_file)
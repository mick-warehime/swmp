from collections import namedtuple

import pygame as pg
import pytweening as tween
from pygame.math import Vector2

from data.input_output import load_mod_data_kwargs
from model import TimeAccess, GameObject
from mods import Mod, BOB_RANGE, BOB_PERIOD, BOB_SPEED, ModData
from view import images

BaseItemData = namedtuple('BaseItemData', ('mod_data', 'image_file'))


class ItemData(BaseItemData):
    def __new__(cls, mod_label: str, image_file: str) -> None:
        mod_data = ModData(**load_mod_data_kwargs(mod_label))

        return super().__new__(cls, mod_data, image_file)


class ItemObject(GameObject, TimeAccess):
    """A bobbing in-game object that can be picked up."""

    def __init__(self, mod: Mod, pos: Vector2) -> None:
        GameObject.__init__(self, pos)
        TimeAccess.__init__(self)

        mygroups = [self.groups.all_sprites, self.groups.items]
        pg.sprite.Sprite.__init__(self, mygroups)

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


class ItemFromData(ItemObject):
    def __init__(self, item_data: ItemData, pos: Vector2) -> None:
        mod = Mod(item_data.mod_data)
        self._image_file = item_data.image_file
        super().__init__(mod, pos)

    @property
    def image(self) -> pg.Surface:
        return images.get_image(self._image_file)

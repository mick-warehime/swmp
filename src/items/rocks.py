"""Module implementing Rock projectile weapon."""

import pygame as pg
from pygame.math import Vector2

import images
from data.mods_io import load_mod_data

from mods import Mod
from items_module import ItemObject


class RockObject(ItemObject):
    rock_size = (15, 15)

    def __init__(self, pos: Vector2) -> None:
        self._check_class_initialized()

        mod = Mod(load_mod_data('rock'))

        super().__init__(mod, pos)

    @property
    def image(self) -> pg.Surface:
        image = images.get_image(images.ROCK)
        return pg.transform.scale(image, self.rock_size)

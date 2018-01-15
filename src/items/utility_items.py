import pygame as pg
from pygame.math import Vector2

import images

from data.mods_io import load_mod_data
from mods import ItemObject, Mod


class HealthPackObject(ItemObject):
    def __init__(self, pos: Vector2) -> None:
        self._check_class_initialized()

        mod = Mod(load_mod_data('healthpack'))

        super().__init__(mod, pos)

    @property
    def image(self) -> pg.Surface:
        return images.get_image(images.HEALTH_PACK)


class Battery(ItemObject):
    def __init__(self, pos: Vector2) -> None:
        self._check_class_initialized()
        mod = Mod(load_mod_data('battery'))

        super().__init__(mod, pos)

    @property
    def image(self) -> pg.Surface:
        return images.get_image(images.ENERGY_PACK)

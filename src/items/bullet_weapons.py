import pygame as pg
from pygame.math import Vector2

import images
from data.mods_io import load_mod_data
from mods import ItemObject, Mod
from projectiles import MuzzleFlash


class PistolObject(ItemObject):
    def __init__(self, pos: Vector2) -> None:
        self._check_class_initialized()

        mod = Mod(load_mod_data('pistol'))

        super().__init__(mod, pos)

    @property
    def image(self) -> pg.Surface:
        return images.get_image(images.PISTOL)


def make_flash(origin: Vector2) -> None:
    MuzzleFlash(origin)


class ShotgunObject(ItemObject):
    def __init__(self, pos: Vector2) -> None:
        self._check_class_initialized()

        mod = Mod(load_mod_data('shotgun'))

        super().__init__(mod, pos)

    @property
    def image(self) -> pg.Surface:
        return images.get_image(images.SHOTGUN)

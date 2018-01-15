from random import randint

import pygame as pg
from pygame.math import Vector2

import images
import settings
from data.abilities_io import load_ability_data
from model import DynamicObject
from mods import ModLocation, ItemObject, ModData, Mod


class MuzzleFlash(DynamicObject):
    def __init__(self, pos: Vector2) -> None:
        self._check_class_initialized()
        pg.sprite.Sprite.__init__(self, self._groups.all_sprites)
        super().__init__(pos)
        self._rect = self.image.get_rect().copy()
        self._rect.center = self.pos
        self._spawn_time = self._timer.current_time

    def update(self) -> None:
        if self._fade_out():
            self.kill()

    @property
    def image(self) -> pg.Surface:
        size = randint(20, 50)
        flash_img = images.get_muzzle_flash()
        return pg.transform.scale(flash_img, (size, size))

    def _fade_out(self) -> bool:
        time_elapsed = self._timer.current_time - self._spawn_time
        return time_elapsed > settings.FLASH_DURATION

    @property
    def rect(self) -> pg.Rect:
        return self._rect


class PistolObject(ItemObject):
    def __init__(self, pos: Vector2) -> None:
        self._check_class_initialized()

        ability_data = load_ability_data('pistol')

        mod_data = ModData(ModLocation.ARMS, ability_data, images.PISTOL_MOD,
                           images.PISTOL, 'pistol')

        mod = Mod(mod_data)

        super().__init__(mod, pos)

    @property
    def image(self) -> pg.Surface:
        return images.get_image(images.PISTOL)


def make_flash(origin: Vector2) -> None:
    MuzzleFlash(origin)


class ShotgunObject(ItemObject):
    def __init__(self, pos: Vector2) -> None:
        self._check_class_initialized()

        ability_data = load_ability_data('shotgun')
        mod_data = ModData(ModLocation.ARMS, ability_data, images.SHOTGUN_MOD,
                           images.SHOTGUN, 'shotgun')

        mod = Mod(mod_data)

        super().__init__(mod, pos)

    @property
    def image(self) -> pg.Surface:
        return images.get_image(images.SHOTGUN)

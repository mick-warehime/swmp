from random import randint

import pygame as pg
from pygame.math import Vector2

import images
import settings
import sounds
from abilities import ProjectileAbilityData
from data.input_output import load_projectile_data
from model import DynamicObject
from mods import ModLocation, ItemObject, ModData, Mod
from tilemap import ObjectType


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


def pistol_fire_sound(origin: Vector2) -> None:
    sounds.fire_weapon_sound(ObjectType.PISTOL)


class PistolObject(ItemObject):
    def __init__(self, pos: Vector2) -> None:
        self._check_class_initialized()

        projectile_data = load_projectile_data('bullet')

        ability_data = ProjectileAbilityData(250,
                                             projectile_data=projectile_data,
                                             projectile_count=1,
                                             kickback=200, spread=5,
                                             fire_effects=[make_flash,
                                                           pistol_fire_sound])

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

        projectile_data = load_projectile_data('little_bullet')
        ability_data = ProjectileAbilityData(900,
                                             projectile_data=projectile_data,
                                             projectile_count=12,
                                             kickback=300, spread=20,
                                             fire_effects=[pistol_fire_sound,
                                                           make_flash])
        mod_data = ModData(ModLocation.ARMS, ability_data, images.SHOTGUN_MOD,
                           images.SHOTGUN, 'shotgun')

        mod = Mod(mod_data)

        super().__init__(mod, pos)

    @property
    def image(self) -> pg.Surface:
        return images.get_image(images.SHOTGUN)

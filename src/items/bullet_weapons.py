from random import randint
from typing import List

import pygame as pg
from pygame.math import Vector2

import images
import settings
import sounds
from abilities import Ability, ProjectileAbilityData, FireProjectile
from model import DynamicObject
from mods import Mod, ModLocation, Buffs, Proficiencies, ItemObject
from tilemap import ObjectType
from projectiles import ProjectileData


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


def pistol_fire_effect(origin: Vector2) -> None:
    sounds.fire_weapon_sound(ObjectType.PISTOL)
    MuzzleFlash(origin)


class ShotgunMod(Mod):
    loc = ModLocation.ARMS

    def __init__(self, buffs: List[Buffs] = None,
                 perks: List[Proficiencies] = None) -> None:
        super().__init__(buffs, perks)

        projectile_data = ProjectileData(hits_player=False, damage=25,
                                         speed=500,
                                         max_lifetime=500,
                                         image_file=images.LITTLE_BULLET)
        ability_data = ProjectileAbilityData(900, projectile_data=projectile_data,
                                             projectile_count=12,
                                             kickback=300, spread=20,
                                             fire_effect=pistol_fire_effect)

        self._ability = FireProjectile(ability_data)

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

    @property
    def description(self) -> str:
        return 'Shotgun'


class PistolMod(Mod):
    loc = ModLocation.ARMS

    def __init__(self, buffs: List[Buffs] = None,
                 perks: List[Proficiencies] = None) -> None:
        super().__init__(buffs, perks)

        projectile_data = ProjectileData(hits_player=False, damage=75,
                                         speed=1000,
                                         max_lifetime=400,
                                         image_file=images.BULLET_IMG)
        ability_data = ProjectileAbilityData(250, projectile_data=projectile_data,
                                             projectile_count=1,
                                             kickback=200, spread=5,
                                             fire_effect=pistol_fire_effect)

        self._ability = FireProjectile(ability_data)

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

    @property
    def description(self) -> str:
        return 'Pistol'


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

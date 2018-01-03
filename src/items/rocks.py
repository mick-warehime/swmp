"""Module implementing Rock projectile weapon."""
from typing import List

import pygame as pg
from pygame.math import Vector2

import images
import sounds
from abilities import FireProjectile, Ability
from mods import ItemObject, Mod, ModLocation, Buffs, Proficiencies
from tilemap import ObjectType
from weapons import Projectile


class Rock(Projectile):
    max_lifetime = 800
    speed = 250
    damage = 25
    rock_size = (10, 10)

    @property
    def image(self) -> pg.Surface:
        angle = self._timer.current_time // 2 % 360
        image = images.get_image(images.ROCK)
        image = pg.transform.rotate(image, angle)

        return pg.transform.scale(image, self.rock_size)

    def kill(self) -> None:
        RockObject(self.pos)
        super().kill()


class ThrowRock(FireProjectile):
    _kickback = 0
    _cool_down_time = 500
    _spread = 10
    _projectile_count = 1
    _make_projectile = Rock

    def __init__(self) -> None:
        super().__init__()
        self.uses_left = 1

    def _fire_effects(self, origin: Vector2) -> None:
        sounds.fire_weapon_sound(ObjectType.ROCK)
        self.uses_left -= 1


class RockMod(Mod):
    loc = ModLocation.ARMS

    def __init__(self, buffs: List[Buffs] = None,
                 profs: List[Proficiencies] = None) -> None:
        super().__init__(buffs, profs)
        self._ability = ThrowRock()

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
    def description(self) -> str:
        uses_left = self._ability.uses_left
        if uses_left == 1:
            return 'Rock'
        else:
            return '%d rocks' % (uses_left,)

    @property
    def equipped_image(self) -> pg.Surface:
        return images.get_image(images.ROCK)

    @property
    def backpack_image(self) -> pg.Surface:
        return images.get_image(images.ROCK)


class RockObject(ItemObject):
    rock_size = (15, 15)

    def __init__(self, pos: Vector2) -> None:
        self._check_class_initialized()
        mod = RockMod()

        super().__init__(mod, pos)

    @property
    def image(self) -> pg.Surface:
        image = images.get_image(images.ROCK)
        return pg.transform.scale(image, self.rock_size)

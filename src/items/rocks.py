"""Module implementing Rock projectile weapon."""
from typing import List

import pygame as pg
from pygame.math import Vector2

from abilities import Ability, ProjectileAbilityData, FireProjectile
import images
from mods import ItemObject, Mod, ModLocation, Buffs, Proficiencies
from sounds import fire_weapon_sound
from tilemap import ObjectType
from projectiles import ProjectileData


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


def throw_rock_effect(origin: Vector2) -> None:
    fire_weapon_sound(ObjectType.ROCK)


class RockMod(Mod):
    loc = ModLocation.ARMS

    def __init__(self, buffs: List[Buffs] = None,
                 profs: List[Proficiencies] = None) -> None:
        super().__init__(buffs, profs)

        projectile_data = ProjectileData(hits_player=False, damage=25,
                                         speed=250,
                                         max_lifetime=800,
                                         image_file=images.LITTLE_ROCK,
                                         rotating_image=True,
                                         drops_on_kill=RockObject)
        ability_data = ProjectileAbilityData(500,projectile_data=projectile_data, spread=2,
                                             fire_effect=throw_rock_effect,
                                             finite_uses=True, uses_left=1)

        self._ability = FireProjectile(ability_data)

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

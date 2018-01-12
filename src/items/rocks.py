"""Module implementing Rock projectile weapon."""
from typing import List

import pygame as pg
from pygame.math import Vector2

from abilities import Ability, ProjectileAbilityData, FireProjectile
import images
from mods import ItemObject, Mod, ModLocation, Buffs, Proficiencies, ModData, \
    ModFromData
from sounds import fire_weapon_sound
from tilemap import ObjectType
from projectiles import ProjectileData


class RockObject(ItemObject):
    rock_size = (15, 15)

    def __init__(self, pos: Vector2) -> None:
        self._check_class_initialized()

        projectile_data = ProjectileData(hits_player=False, damage=25,
                                         speed=250,
                                         max_lifetime=800,
                                         image_file=images.LITTLE_ROCK,
                                         rotating_image=True,
                                         drops_on_kill=RockObject)
        ability_data = ProjectileAbilityData(500,
                                             projectile_data=projectile_data,
                                             spread=2,
                                             fire_effects=[throw_rock_effect],
                                             finite_uses=True, uses_left=1)
        mod_data = ModData(ModLocation.ARMS, ability_data, images.ROCK,
                           images.ROCK, 'Rock', True)

        mod = ModFromData(mod_data)

        super().__init__(mod, pos)

    @property
    def image(self) -> pg.Surface:
        image = images.get_image(images.ROCK)
        return pg.transform.scale(image, self.rock_size)


def throw_rock_effect(origin: Vector2) -> None:
    fire_weapon_sound(ObjectType.ROCK)

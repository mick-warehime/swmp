"""Module implementing Rock projectile weapon."""

import pygame as pg
from pygame.math import Vector2

import images
from data.abilities_io import load_ability_data

from mods import ItemObject, ModLocation, ModData, Mod
from sounds import fire_weapon_sound
from tilemap import ObjectType


class RockObject(ItemObject):
    rock_size = (15, 15)

    def __init__(self, pos: Vector2) -> None:
        self._check_class_initialized()

        ability_data = load_ability_data('rock')
        mod_data = ModData(ModLocation.ARMS, ability_data, images.ROCK,
                           images.ROCK, 'Rock', True)

        mod = Mod(mod_data)

        super().__init__(mod, pos)

    @property
    def image(self) -> pg.Surface:
        image = images.get_image(images.ROCK)
        return pg.transform.scale(image, self.rock_size)


def throw_rock_effect(origin: Vector2) -> None:
    fire_weapon_sound(ObjectType.ROCK)

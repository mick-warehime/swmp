import pygame as pg
from pygame.math import Vector2

import images

from data.abilities_io import load_ability_data
from mods import ModLocation, ItemObject, ModData, Mod


class HealthPackObject(ItemObject):
    def __init__(self, pos: Vector2) -> None:
        self._check_class_initialized()

        ability_data = load_ability_data('basic_heal')
        mod_data = ModData(ModLocation.CHEST, ability_data, images.HEALTH_PACK,
                           images.HEALTH_PACK, 'healthpack', True)

        mod = Mod(mod_data)

        super().__init__(mod, pos)

    @property
    def image(self) -> pg.Surface:
        return images.get_image(images.HEALTH_PACK)


class Battery(ItemObject):
    def __init__(self, pos: Vector2) -> None:
        self._check_class_initialized()
        ability_data = load_ability_data('basic_recharge')
        mod_data = ModData(ModLocation.CHEST, ability_data, images.LIGHTNING,
                           images.ENERGY_PACK, 'battery', True)

        mod = Mod(mod_data)

        super().__init__(mod, pos)

    @property
    def image(self) -> pg.Surface:
        return images.get_image(images.ENERGY_PACK)

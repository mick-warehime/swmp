import pygame as pg
from pygame.math import Vector2

import images
from abilities import RegenerationAbilityData
from mods import ModLocation, ItemObject, ModData, Mod

BATTERY_AMOUNT = 50
HEALTH_PACK_AMOUNT = 20


class HealthPackObject(ItemObject):
    def __init__(self, pos: Vector2) -> None:
        self._check_class_initialized()

        ability_data = RegenerationAbilityData(cool_down_time=300,
                                               finite_uses=True,
                                               uses_left=1,
                                               heal_amount=HEALTH_PACK_AMOUNT)
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
        ability_data = RegenerationAbilityData(cool_down_time=300,
                                               finite_uses=True,
                                               uses_left=1,
                                               recharge_amount=BATTERY_AMOUNT)
        mod_data = ModData(ModLocation.CHEST, ability_data, images.LIGHTNING,
                           images.ENERGY_PACK, 'battery', True)

        mod = Mod(mod_data)

        super().__init__(mod, pos)

    @property
    def image(self) -> pg.Surface:
        return images.get_image(images.ENERGY_PACK)

from typing import List, Union, Any

import pygame as pg
from pygame.math import Vector2

import images
from abilities import Ability, RegenerationAbilityData, RegenerationAbility
from mods import Mod, ModLocation, Buffs, Proficiencies, HEALTH_PACK_AMOUNT, \
    ItemObject


class HealthPackMod(Mod):
    loc = ModLocation.CHEST

    def __init__(self, buffs: List[Buffs] = None,
                 perks: List[Proficiencies] = None) -> None:
        super().__init__(buffs, perks)
        self._expended = False

        data = RegenerationAbilityData(cool_down_time=300, finite_uses=True,
                                       uses_left=1,
                                       heal_amount=HEALTH_PACK_AMOUNT)
        self._ability = RegenerationAbility(data)

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
    def backpack_image(self) -> pg.Surface:
        return images.get_image(images.HEALTH_PACK)

    @property
    def equipped_image(self) -> pg.Surface:
        return images.get_image(images.HEALTH_PACK)

    @property
    def description(self) -> str:
        return 'Healthpack'


class HealthPackObject(ItemObject):
    def __init__(self, pos: Vector2) -> None:
        self._check_class_initialized()
        mod = HealthPackMod()

        super().__init__(mod, pos)

    @property
    def image(self) -> pg.Surface:
        return images.get_image(images.HEALTH_PACK)

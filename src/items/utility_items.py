from typing import List, Union, Any

import pygame as pg
from pygame.math import Vector2

import images
import sounds
from abilities import Ability
from mods import Mod, ModLocation, Buffs, Proficiencies, HEALTH_PACK_AMOUNT, \
    ItemObject


class Heal(Ability):
    """A healing ability with a timed cooldown and finite use count."""
    _cool_down_time: Union[int, None] = 300

    def __init__(self, num_uses: int, heal_amount: int) -> None:
        super().__init__()
        self.uses_left = num_uses
        self._heal_amount = heal_amount

    @property
    def can_use(self) -> bool:
        can_use = super().can_use
        can_use = can_use and self.uses_left > 0
        return can_use

    def use(self, humanoid: Any) -> None:
        if humanoid.damaged:
            self._update_last_use()
            self.uses_left -= 1
            sounds.play(sounds.HEALTH_UP)
            humanoid.increment_health(self._heal_amount)


class HealthPackMod(Mod):
    loc = ModLocation.CHEST

    def __init__(self, buffs: List[Buffs] = None,
                 perks: List[Proficiencies] = None) -> None:
        super().__init__(buffs, perks)
        self._expended = False
        self._ability = Heal(1, HEALTH_PACK_AMOUNT)

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

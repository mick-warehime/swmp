from collections import namedtuple
from enum import Enum
from typing import Set, Any

import pygame as pg

import images
from abilities import Ability, GenericAbility
from data.abilities_io import load_ability_data

BOB_RANGE = 1
BOB_SPEED = 0.3
BOB_PERIOD = 10

NO_MOD_AT_LOCATION = -1


class ModLocation(Enum):
    __order__ = 'ARMS LEGS CHEST HEAD'
    ARMS = 'arms'
    LEGS = 'legs'
    CHEST = 'chest'
    HEAD = 'head'


class Buffs(Enum):
    ARMOR = 'armor'
    DAMAGE = 'damage'
    RANGE = 'range'


class Proficiencies(Enum):
    TALKING = 'talking'
    STEALTH = 'stealth'
    ATHLETICISM = 'athleticism'


BaseModData = namedtuple('BaseModData',
                         ('location', 'ability_data', 'equipped_image',
                          'backpack_image', 'description', 'stackable',
                          'buffs', 'proficiencies'))


class ModData(BaseModData):
    def __new__(cls, location: str, ability_label: str,
                equipped_image_file: str, backpack_image_file: str,
                description: str, stackable: bool = False,
                buffs: Set[Buffs] = None,
                proficiencies: Set[Proficiencies] = None) -> BaseModData:
        ability_data = load_ability_data(ability_label)

        return super().__new__(cls, ModLocation(location),  # type: ignore
                               ability_data, equipped_image_file,
                               backpack_image_file, description, stackable,
                               buffs, proficiencies)


class Mod(object):
    def __init__(self, data: ModData) -> None:
        self._data = data
        self._buffs = data.buffs
        self._profs = data.proficiencies

        self._ability = GenericAbility(data.ability_data)

    @property
    def loc(self) -> ModLocation:
        return self._data.location

    @property
    def expended(self) -> bool:
        if self._data.ability_data.finite_uses:
            return self._ability.uses_left <= 0
        return False

    @property
    def ability(self) -> Ability:
        return self._ability

    @property
    def equipped_image(self) -> pg.Surface:
        return images.get_image(self._data.equipped_image)

    @property
    def backpack_image(self) -> pg.Surface:
        return images.get_image(self._data.backpack_image)

    @property
    def description(self) -> str:
        description = self._data.description
        if self._ability.finite_uses:
            description += '({} uses left)'.format(self._ability.uses_left)
        return description

    @property
    def stackable(self) -> bool:
        return self._data.stackable

    def __eq__(self, other: Any) -> bool:  # type: ignore
        if not isinstance(other, type(self)):
            return False
        return self._data == other._data

    def __str__(self) -> str:
        output = '%s' % (self.description)
        if self._buffs or self._profs:
            output += '('
            for buff in self._buffs:
                output += '%s, ' % (buff.value,)
            for prof in self._profs:
                output += '%s, ' % (prof.value,)
            output += ')'
        return output



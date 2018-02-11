"""Possible resolutions to dramatic questions."""
import abc
from enum import Enum
from typing import Dict, Set

from pygame.sprite import Group, Sprite, spritecollide

from conditions import Condition
from model import GameObject


class ResolutionType(Enum):
    KILL = 'kill'


class Resolution(abc.ABC):
    @property
    def is_resolved(self) -> bool:
        raise NotImplementedError

    @abc.abstractmethod
    def load_data(self, res_data: Dict[str, Set[Sprite]]) -> None:
        pass


def add_sprites_of_label(label: str, res_data: Dict[str, Set[Sprite]],
                         group: Group) -> None:
    group.add(*res_data[label])


class KillGroup(Resolution):
    def __init__(self, group_label: str):
        self._group_label = group_label
        self._group_to_kill = Group()

    @property
    def is_resolved(self) -> bool:
        return len(self._group_to_kill) == 0

    def load_data(self, res_data: Dict[str, Set[Sprite]]) -> None:
        add_sprites_of_label(self._group_label, res_data, self._group_to_kill)


class EnterZone(Resolution):
    def __init__(self, zone_label: str, entering_label: str):
        self._zone_label = zone_label
        self._entering_label = entering_label
        self._zone_group = Group()
        self._entering_group = Group()

    @property
    def is_resolved(self) -> bool:
        return any(spritecollide(sprite, self._zone_group, False) for
                   sprite in self._entering_group)

    def load_data(self, res_data: Dict[str, Set[Sprite]]) -> None:
        add_sprites_of_label(self._zone_label, res_data, self._zone_group)
        add_sprites_of_label(self._entering_label, res_data,
                             self._entering_group)


class ConditionSatisfied(Resolution):
    def __init__(self, tested_label: str, condition: Condition):
        self._label = tested_label
        self._condition = condition
        self._tested: GameObject = None

    def load_data(self, res_data: Dict[str, Set[Sprite]]) -> None:
        labeled_sprites = res_data[self._label]
        if len(labeled_sprites) != 1:
            raise ValueError(
                'Condition resolution %s requires exactly one GameObject with '
                'label {}'.format(self._condition, self._label))
        self._tested = list(labeled_sprites)[0]

    @property
    def is_resolved(self) -> bool:
        return self._condition.check(self._tested)

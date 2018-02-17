"""Possible resolutions to dramatic questions."""
import abc
from enum import Enum
from typing import Dict, Set, Any

from pygame.sprite import Group, Sprite, spritecollide

from conditions import Condition, condition_from_data
from model import GameObject


class ResolutionType(Enum):
    KILL_GROUP = 'kill group'
    ENTER_ZONE = 'enter zone'
    CONDITION = 'condition'
    DECISION_CHOICE = 'decision choice'


class Resolution(abc.ABC):
    @property
    def is_resolved(self) -> bool:
        raise NotImplementedError

    @abc.abstractmethod
    def load_sprite_data(self,
                         sprite_categories: Dict[str, Set[Sprite]]) -> None:
        pass


def add_sprites_of_label(label: str, res_data: Dict[str, Set[Sprite]],
                         group: Group) -> None:
    group.add(*res_data[label])


class KillGroup(Resolution):
    def __init__(self, group_label: str) -> None:
        self._group_label = group_label
        self._group_to_kill = Group()

    @property
    def is_resolved(self) -> bool:
        return len(self._group_to_kill) == 0

    def load_sprite_data(self,
                         sprite_categories: Dict[str, Set[Sprite]]) -> None:
        add_sprites_of_label(self._group_label, sprite_categories,
                             self._group_to_kill)


class EnterZone(Resolution):
    def __init__(self, zone_label: str, entering_label: str) -> None:
        self._zone_label = zone_label
        self._entering_label = entering_label
        self._zone_group = Group()
        self._entering_group = Group()

    @property
    def is_resolved(self) -> bool:
        return any(spritecollide(sprite, self._zone_group, False) for
                   sprite in self._entering_group)

    def load_sprite_data(self,
                         sprite_categories: Dict[str, Set[Sprite]]) -> None:
        add_sprites_of_label(self._zone_label, sprite_categories,
                             self._zone_group)
        add_sprites_of_label(self._entering_label, sprite_categories,
                             self._entering_group)


class ConditionSatisfied(Resolution):
    def __init__(self, tested_label: str, condition: Condition) -> None:
        self._label = tested_label
        self._condition = condition
        self._tested: GameObject = None

    def load_sprite_data(self,
                         sprite_categories: Dict[str, Set[Sprite]]) -> None:
        labeled_sprites = sprite_categories[self._label]
        if len(labeled_sprites) != 1:
            raise ValueError(
                'Condition resolution %s requires exactly one GameObject with '
                'label {}'.format(self._condition, self._label))
        self._tested = list(labeled_sprites)[0]

    @property
    def is_resolved(self) -> bool:
        return self._condition.check(self._tested)


class MakeDecision(Resolution):
    def __init__(self, description: str) -> None:
        self.description = description
        self._decision_chosen = False

    def choose(self) -> None:
        self._decision_chosen = True

    @property
    def is_resolved(self) -> bool:
        return self._decision_chosen

    def load_sprite_data(self,
                         sprite_categories: Dict[str, Set[Sprite]]) -> None:
        pass

    def __str__(self) -> str:
        return 'MakeDecision {}'.format(self.description)


def resolution_from_data(res_data: Dict[str, Any]) -> Resolution:
    assert len(res_data.keys()) == 1, 'root keys must be the length one, ' \
                                      'matching the resolution label.'
    res_label = list(res_data.keys())[0]
    data = res_data[res_label]
    res_type = ResolutionType(res_label)

    if res_type == ResolutionType.KILL_GROUP:
        group_label = data['group label']
        return KillGroup(group_label)
    elif res_type == ResolutionType.ENTER_ZONE:
        zone_label = data['zone label']
        entering_label = data['entering label']
        return EnterZone(zone_label, entering_label)
    elif res_type == ResolutionType.CONDITION:
        condition_data = data['condition data']
        condition = condition_from_data(condition_data, None, None)
        tested_label = data['tested label']
        return ConditionSatisfied(tested_label, condition)
    elif res_type == ResolutionType.DECISION_CHOICE:
        return MakeDecision(data['description'])
    else:
        raise NotImplementedError('Definition of resolution type {} not yet '
                                  'implemented'.format(res_type))

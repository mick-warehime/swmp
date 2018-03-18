"""Possible resolutions to dramatic questions."""
import abc
from enum import Enum
from typing import Dict, Any, Collection, List, Callable

from pygame.sprite import Group, Sprite, spritecollide

from conditions import condition_from_data
from model import GameObject


class ResolutionType(Enum):
    KILL_GROUP = 'kill group'
    ENTER_ZONE = 'enter zone'
    CONDITION = 'condition'
    DECISION_CHOICE = 'decision choice'

    @property
    def arg_labels(self) -> List[str]:
        return _resolution_args[self]

    @property
    def constructor(self) -> Callable[[Any], 'Resolution']:
        return _resolution_map[self]


class ResolutionModifiers(Enum):
    REQUIRES_TELEPORT = 'requires teleport'

    @classmethod
    def has_value(cls, value) -> bool:
        return any(value == item.value for item in cls)


SpriteLabels = Dict[str, Collection[Sprite]]


class Resolution(abc.ABC):
    """Represents a resolution to a Scene, which signals a change to the next.
    """

    @property
    def is_resolved(self) -> bool:
        raise NotImplementedError

    @abc.abstractmethod
    def load_sprite_data(self, sprite_categories: SpriteLabels) -> None:
        """Called after sprites have been created and categorized from map."""


class RequiresTeleport(Resolution):
    """Decorator pattern for a Resolution requiring player to press `teleport'.
    """

    def __init__(self, base_resolution: Resolution) -> None:
        self._base_resolution = base_resolution
        self._teleport_on = False

    @property
    def is_resolved(self) -> bool:
        # teleport_on is set to False so that is_resolved is True at the
        # instant that teleport_on is set to True.
        teleport_on = self._teleport_on
        self._teleport_on = False
        return self._base_resolution.is_resolved and teleport_on

    def load_sprite_data(self, sprite_categories: SpriteLabels) -> None:
        self._base_resolution.load_sprite_data(sprite_categories)

    def toggle_teleport(self) -> None:
        self._teleport_on = True


def _add_sprites_of_label(label: str, res_data: SpriteLabels,
                          group: Group) -> None:
    group.add(*res_data[label])


class KillGroup(Resolution):
    """Resolves when a group is killed."""

    def __init__(self, group_label: str) -> None:
        self._group_label = group_label
        self._group_to_kill = Group()

    @property
    def is_resolved(self) -> bool:
        return len(self._group_to_kill) == 0

    def load_sprite_data(self, sprite_categories: SpriteLabels) -> None:
        _add_sprites_of_label(self._group_label, sprite_categories,
                              self._group_to_kill)


class EnterZone(Resolution):
    """Resolves when a labeled sprite enters a labeled zone."""

    def __init__(self, zone_label: str, entering_label: str) -> None:
        self._zone_label = zone_label
        self._entering_label = entering_label
        self._zone_group = Group()
        self._entering_group = Group()

    @property
    def is_resolved(self) -> bool:
        return any(spritecollide(sprite, self._zone_group, False) for
                   sprite in self._entering_group)

    def load_sprite_data(self, sprite_categories: SpriteLabels) -> None:
        _add_sprites_of_label(self._zone_label, sprite_categories,
                              self._zone_group)
        _add_sprites_of_label(self._entering_label, sprite_categories,
                              self._entering_group)


class ConditionSatisfied(Resolution):
    """Resolves when a Condition is satisfied on a given sprite."""

    def __init__(self, tested_label: str,
                 condition_data: Dict[str, Any]) -> None:
        self._label = tested_label
        self._condition = condition_from_data(condition_data, None)
        self._tested: GameObject = None

    def load_sprite_data(self, sprite_categories: SpriteLabels) -> None:
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
    """Resolves when the player chooses the described option."""

    def __init__(self, description: str) -> None:
        self.description = description
        self._decision_chosen = False

    def choose(self) -> None:
        self._decision_chosen = True

    @property
    def is_resolved(self) -> bool:
        return self._decision_chosen

    def load_sprite_data(self, sprite_categories: SpriteLabels) -> None:
        pass

    def __str__(self) -> str:
        return 'MakeDecision: {}'.format(self.description)


_resolution_args = {ResolutionType.DECISION_CHOICE: ['description'],
                    ResolutionType.CONDITION:
                        ['tested label', 'condition data'],
                    ResolutionType.ENTER_ZONE:
                        ['zone label', 'entering label'],
                    ResolutionType.KILL_GROUP: ['group label']}

_resolution_map = {ResolutionType.DECISION_CHOICE: MakeDecision,
                   ResolutionType.CONDITION: ConditionSatisfied,
                   ResolutionType.ENTER_ZONE: EnterZone,
                   ResolutionType.KILL_GROUP: KillGroup}

_modifiers_map = {ResolutionModifiers.REQUIRES_TELEPORT: RequiresTeleport}


def resolution_from_data(res_data: Dict[str, Any]) -> Resolution:
    """Constructs a Resolution from a data dictionary."""
    assert len(res_data.keys()) == 1, 'root keys must be the length one, ' \
                                      'matching the resolution label.'
    res_label = list(res_data.keys())[0]
    data = res_data[res_label]
    res_type = ResolutionType(res_label)

    args = [data[key] for key in res_type.arg_labels]
    resolution = res_type.constructor(*args)

    for key in data.keys():
        if ResolutionModifiers.has_value(key):
            modifier = _modifiers_map[ResolutionModifiers(key)]
            resolution = modifier(resolution)

    return resolution

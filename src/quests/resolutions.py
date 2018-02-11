"""Possible resolutions to dramatic questions."""
import abc
from enum import Enum

from pygame.sprite import Group, Sprite


class ResolutionType(Enum):
    KILL = 'kill'


class Resolution(abc.ABC):
    def __init__(self, group_label: str):
        self.group_label = group_label

    @property
    def is_resolved(self) -> bool:
        raise NotImplementedError

    @property
    def resolve_immediately(self) -> bool:
        raise NotImplementedError


class KillGroup(Resolution):
    def __init__(self, group_label: str, resolve_immediately=False):
        super().__init__(group_label)
        self._group_to_kill = Group()
        self._resolve_immediately = resolve_immediately

    def add_to_group(self, *sprites: Sprite) -> None:
        self._group_to_kill.add(*sprites)

    @property
    def is_resolved(self) -> bool:
        return len(self._group_to_kill) == 0

    @property
    def resolve_immediately(self) -> bool:
        return self._resolve_immediately

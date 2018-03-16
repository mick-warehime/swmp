from collections import namedtuple
from typing import Union

import pygame as pg
from pygame.math import Vector2
from pygame.sprite import Group, LayeredUpdates, Sprite

_GroupsBase = namedtuple('_GroupsBase',
                         ('walls', 'bullets', 'enemy_projectiles',
                          'items', 'enemies', 'zones', 'all_sprites'))


class Groups(_GroupsBase):
    """Immutable container object for groups in the game."""

    def __new__(cls) -> _GroupsBase:
        args = [Group() for _ in range(6)]
        args += [LayeredUpdates()]
        return super(Groups, cls).__new__(cls, *args)  # type: ignore

    def empty(self) -> None:
        """Empty each group field."""
        self.walls.empty()
        self.enemies.empty()
        self.bullets.empty()
        self.all_sprites.empty()
        self.items.empty()
        self.zones.empty()
        self.enemy_projectiles.empty()


class Timer(object):
    """Keeps track of game time."""

    def __init__(self, clock: pg.time.Clock) -> None:
        self._clock = clock

    @property
    def dt(self) -> float:
        return self._clock.get_time() / 1000.0

    @property
    def current_time(self) -> int:
        return pg.time.get_ticks()


def initialize(groups: Groups, timer: 'Timer') -> None:
    GroupsAccess.initialize_groups(groups)
    TimeAccess.initialize(timer)


class GroupsAccess(object):
    """An object with access to a `groups' class variable."""

    _groups: Groups = None

    @property
    def groups(self) -> Groups:
        if not self._class_initialized():
            raise RuntimeError('GroupsAccess not initialized.')
        return self._groups

    @classmethod
    def initialize_groups(cls, groups: Groups):
        cls._groups = groups

    @classmethod
    def _class_initialized(cls) -> bool:
        return cls._groups is not None


class GameObject(GroupsAccess, pg.sprite.Sprite):
    """In-game object with a rect for collisions and an image. """

    def __init__(self, pos: Vector2) -> None:
        self.pos = Vector2(pos.x, pos.y)

    @property
    def image(self) -> pg.Surface:
        raise NotImplementedError

    @property
    def rect(self) -> pg.Rect:
        """Rect object used in sprite collisions."""
        raise NotImplementedError


class Obstacle(GroupsAccess, Sprite):
    def __init__(self, top_left: Vector2, w: int, h: int) -> None:
        pg.sprite.Sprite.__init__(self, self.groups.walls)

        self.rect = pg.Rect(top_left.x, top_left.y, w, h)


class Zone(GroupsAccess, Sprite):
    """A region with collisions."""

    def __init__(self, top_left: Vector2, w: int, h: int) -> None:
        pg.sprite.Sprite.__init__(self, self.groups.zones)

        self.rect = pg.Rect(top_left.x, top_left.y, w, h)


class TimeAccess(object):
    """A time-changing GameObject with access to current time information.

    Instructions for subclassing:
    Follow instructions for GameObject.

    TimeAccess.initialize_dynamic_objects() must be called before
    instantiating any subclasses.
    """

    _timer: Union[Timer, None] = None

    @classmethod
    def initialize(cls, timer: Timer) -> None:
        cls._timer = timer

    @property
    def timer(self) -> Timer:
        if self._timer is None:
            raise RuntimeError('TimeAccess not initialized.')
        return self._timer

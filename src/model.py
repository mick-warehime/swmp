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


def initialize_groups(groups: Groups) -> None:
    GameObject.initialize_gameobjects(groups)
    GroupsAccess.initialize_groups(groups)


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


class GroupsAccess(object):
    """An object with access to a `groups' class variable."""

    _groups: Groups = None

    @property
    def groups(self) -> Groups:
        assert self._check_class_initialized(), 'GroupsAccess not initialized.'
        return self._groups

    @classmethod
    def initialize_groups(cls, groups: Groups):
        cls._groups = groups

    @classmethod
    def _check_class_initialized(cls) -> None:
        return cls._groups is not None


class GameObject(pg.sprite.Sprite):
    """In-game object with a rect for collisions and an image.

    Added functionality derived from Sprite:
    Can be added/removed to Group objects --> add(*groups), remove(*groups).
    kill() removes from all groups.
    update() method that is referenced when a group is updated.
    alive() : True iff sprite belongs to any group.

    Instructions for subclassing GameObject:

    In the __init__:
      Make sure to call `self._check_class_initialized()'
      Before calling super().__init__(pos), make sure that all attributes
      necessary to access the image property are initialized.

    Implement the abstact property image.

    Note:
      By default, the rect attribute will be a copy of the image's original
      rect.

    GameObject.initialize_gameobjects() must be called before instantiating any
    subclasses.
    """
    gameobjects_initialized = False
    _groups: Groups = None

    def __init__(self, pos: Vector2) -> None:
        self._check_class_initialized()

        self.pos = Vector2(pos.x, pos.y)

    def _check_class_initialized(self) -> None:
        if not self.gameobjects_initialized:
            raise RuntimeError('GameObject class must be initialized before '
                               'instantiating a GameObject.')

    @classmethod
    def initialize_gameobjects(cls, groups: Groups) -> None:
        cls._groups = groups
        cls.gameobjects_initialized = True

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


class DynamicObject(GameObject):
    """A time-changing GameObject with access to current time information.

    Instructions for subclassing:
    Follow instructions for GameObject.

    DynamicObject.initialize_dynamic_objects() must be called before
    instantiating any subclasses.
    """
    dynamic_initialized = False
    _timer: Union[Timer, None] = None

    @classmethod
    def initialize_dynamic_objects(cls, timer: Timer) -> None:
        cls._timer = timer
        cls.dynamic_initialized = True

    def _check_class_initialized(self) -> None:
        super()._check_class_initialized()
        if not self.dynamic_initialized:
            raise RuntimeError('DynamicObject class must be initialized before'
                               ' instantiating a DynamicObject.')

    @property
    def rect(self) -> pg.Rect:
        raise NotImplementedError

    @property
    def image(self) -> pg.Surface:
        raise NotImplementedError

# waypoint objects appear as blue spirals on the map (for now).
# when the player runs into one of these objects they dissappear from the game
# they can serve as the end of a dungeon or as an area that must be explored

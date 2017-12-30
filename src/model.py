from collections import namedtuple
from typing import Any, Union, Dict
import pygame as pg
from pygame.math import Vector2
from pygame.sprite import Group, LayeredUpdates

import images
from settings import TILESIZE

NO_RESOLUTIONS = -69

_GroupsBase = namedtuple('_GroupsBase',
                         ('walls', 'bullets', 'enemy_projectiles',
                          'items', 'mobs', 'all_sprites'))


class Groups(_GroupsBase):
    """Immutable container object for groups in the game."""

    def __new__(cls) -> _GroupsBase:
        args = [Group() for _ in range(5)]
        args += [LayeredUpdates()]
        return super(Groups, cls).__new__(cls, *args)  # type: ignore

    def empty(self) -> None:
        """Empty each group field."""
        self.walls.empty()
        self.mobs.empty()
        self.bullets.empty()
        self.all_sprites.empty()
        self.items.empty()
        self.enemy_projectiles.empty()


class ConflictGroups(object):
    def __init__(self) -> None:
        self.conflicts: Dict[str, Conflict] = {}

    def number_of_conflicts(self) -> int:
        return len(self.conflicts.keys())

    def get_group(self, conflict_name: str) -> Group:
        if conflict_name not in self.conflicts:
            self.conflicts[conflict_name] = Conflict()
        conflict = self.conflicts[conflict_name]
        return conflict.group

    def any_resolved_conflict(self) -> bool:
        for conflict_name in self.conflicts:
            conflict = self.conflicts[conflict_name]
            if conflict.is_resolved():
                return True
        return False

    def resolved_conflict(self) -> int:
        for conflict_name in self.conflicts:
            conflict = self.conflicts[conflict_name]
            if conflict.is_resolved():
                return int(conflict_name)
        return NO_RESOLUTIONS



class Conflict(object):
    def __init__(self) -> None:
        self.group = Group()

    def is_resolved(self) -> bool:
        return len(self.group) == 0


class Timer(object):
    """Keeps track of game time."""

    def __init__(self, controller: Any) -> None:
        self._dungeon_controller = controller

    @property
    def dt(self) -> float:
        return self._dungeon_controller.dt

    @property
    def current_time(self) -> int:
        return pg.time.get_ticks()


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
    _groups: Union[Groups, None] = None

    def __init__(self, pos: Vector2) -> None:
        self._check_class_initialized()

        self.pos = Vector2(pos.x, pos.y)
        # Used in sprite collisions
        self.rect: pg.Rect = self.image.get_rect().copy()
        self.rect.center = Vector2(pos.x, pos.y)

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


class Obstacle(GameObject):
    def __init__(self, top_left: Vector2, w: int, h: int) -> None:
        self._check_class_initialized()
        pg.sprite.Sprite.__init__(self, self._groups.walls)

        self.rect = pg.Rect(top_left.x, top_left.y, w, h)

    @property
    def image(self) -> pg.Surface:
        raise RuntimeError('Obstacle image is meant to be drawn in the '
                           'background.')

    def update(self) -> None:
        raise RuntimeError('Obstacle is not meant to be updated.')


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
    def image(self) -> pg.Surface:
        raise NotImplementedError


# waypoint objects appear as blue spirals on the map (for now).
# when the player runs into one of these objects they dissappear from the game
# they can serve as the end of a dungeon or as an area that must be explored
class Waypoint(DynamicObject):
    _image = None

    def __init__(self, pos: Vector2, player: Any,
                 conflict_group: Group) -> None:
        super().__init__(pos)
        self.player = player

        if conflict_group is None:
            raise ValueError('missing conflict for waypoint at %s', str(pos))

        waypoint_groups = [self._groups.all_sprites,
                           self._groups.items,
                           conflict_group]

        pg.sprite.Sprite.__init__(self, waypoint_groups)

    def update(self) -> None:
        if self.rect.colliderect(self.player.rect):
            self.kill()

    @property
    def image(self) -> pg.Surface:
        if Waypoint._image is None:
            img = images.get_image(images.WAYPOINT_IMG)
            Waypoint._image = pg.transform.scale(img, (TILESIZE, TILESIZE))
        return self._image

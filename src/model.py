from collections import namedtuple
from typing import Any, Union

import pygame as pg
from pygame.math import Vector2
from pygame.sprite import Group, LayeredUpdates

import images

_GroupsBase = namedtuple('_GroupsBase',
                         ('walls', 'bullets',
                          'items', 'mobs',
                          'conflicts', 'all_sprites'))


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
        self.conflicts.empty()


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
    """In-game object with a hit_rect and rect for collisions and an image.

    Added functionality derived from Sprite:
    Can be added/removed to Group objects --> add(*groups), remove(*groups).
    kill() removes from all groups.
    update() method that is referenced when a group is updated.
    alive() : True iff sprite belongs to any group.

    """
    base_image: Union[pg.Surface, None] = None
    gameobjects_initialized = False
    _groups: Union[Groups, None] = None

    def __init__(self, pos: Vector2) -> None:

        self._check_class_initialized()

        self.image = self.base_image
        self.pos = pos
        # Used in sprite collisions other than walls.
        self.rect: pg.Rect = self.image.get_rect()
        self.rect.center = pos

    def _check_class_initialized(self) -> None:
        if not self.gameobjects_initialized:
            raise RuntimeError('GameObject class must be initialized before '
                               'instantiating a GameObject.')

    @classmethod
    def _init_base_image(cls, image_file: str) -> None:
        if cls.base_image is None:
            cls.base_image = images.get_image(image_file)

    @classmethod
    def initialize_gameobjects(cls, groups: Groups) -> None:
        cls._groups = groups
        cls.gameobjects_initialized = True


class Obstacle(GameObject):
    def __init__(self, pos: Vector2, w: int, h: int) -> None:
        self._check_class_initialized()
        pg.sprite.Sprite.__init__(self, self._groups.walls)

        self.rect = pg.Rect(pos.x, pos.y, w, h)

    @property
    def x(self) -> int:
        return self.rect.x

    @property
    def y(self) -> int:
        return self.rect.y

    @property
    def hit_rect(self) -> pg.Rect:
        return self.rect


class DynamicObject(GameObject):
    """A time-changing GameObject with access to current time information."""
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


# waypoint objects appear as blue spirals on the map (for now).
# when the player runs into one of these objects they dissappear from the game
# they can serve as the end of a dungeon or as an area that must be explored
class Waypoint(DynamicObject):
    def __init__(self, pos: Vector2, player: Any) -> None:
        img = images.get_image(images.WAYPOINT_IMG)
        base_image = pg.transform.scale(img, (50, 50))
        self.base_image = base_image

        super().__init__(pos)
        self.player = player

        waypoint_groups = [self._groups.all_sprites, self._groups.conflicts]
        pg.sprite.Sprite.__init__(self, waypoint_groups)

    def update(self) -> None:
        if self.rect.colliderect(self.player.rect):
            self.kill()

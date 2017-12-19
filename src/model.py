import pygame as pg
from typing import Any, Union
from pygame.math import Vector2
from pygame.sprite import Group, LayeredUpdates
import pytweening as tween
import settings
import images
from collections import namedtuple
import sounds

_GroupsBase = namedtuple('_GroupsBase',
                         ('walls', 'bullets', 'items', 'mobs', 'all_sprites'))


class Groups(_GroupsBase):
    """Immutable container object for groups in the game."""

    def __new__(cls) -> _GroupsBase:
        args = [Group() for _ in range(4)]
        args += [LayeredUpdates()]
        return super(Groups, cls).__new__(cls, *args)  # type: ignore


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
    """In-game object with a body for collisions and an image.

    Added functionality derived from Sprite:
    Can be added/removed to Group objects --> add(*groups), remove(*groups).
    kill() removes from all groups.
    update() method that is referenced when a group is updated.
    alive() : True iff sprite belongs to any group.

    """
    base_image: Union[pg.Surface, None] = None
    gameobjects_initialized = False
    _groups: Union[Groups, None] = None

    def __init__(self, hit_rect: pg.Rect, pos: Vector2) -> None:

        self._check_class_initialized()

        self.image = self.base_image
        self.pos = pos
        # Used in sprite collisions other than walls.
        self.rect: pg.Rect = self.image.get_rect()
        self.rect.center = (pos.x, pos.y)

        # Used in wall collisions
        self.hit_rect = hit_rect.copy()
        self.hit_rect.center = self.rect.center

    def _check_class_initialized(self) -> None:
        if not self.gameobjects_initialized:
            raise ValueError('GameObjects class must be initialized before '
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


class Item(pg.sprite.Sprite):
    def __init__(self, groups: Groups, pos: pg.math.Vector2,
                 label: str) -> None:
        pg.sprite.Sprite.__init__(self, [groups.all_sprites, groups.items])

        self.image = images.get_item_image(label)
        self.rect = self.image.get_rect()
        self.label = label
        self.pos = pos
        self.rect.center = pos
        self.tween = tween.easeInOutSine
        self.step = 0
        self.dir = 1

    def update(self) -> None:
        # bobbing motion
        offset = settings.BOB_RANGE * (
            self.tween(self.step / settings.BOB_RANGE) - 0.5)
        self.rect.centery = self.pos.y + offset * self.dir
        self.step += settings.BOB_SPEED
        if self.step > settings.BOB_RANGE:
            self.step = 0
            self.dir *= -1

    def use(self, player: Any) -> bool:
        raise NotImplementedError


class HealthPack(Item):
    def __init__(self, groups: Groups, pos: pg.math.Vector2,
                 label: str) -> None:
        super(HealthPack, self).__init__(groups, pos, label)

    def use(self, player: Any) -> bool:
        if player.health < settings.PLAYER_HEALTH:
            sounds.play(sounds.HEALTH_UP)
            player.increment_health(settings.HEALTH_PACK_AMOUNT)
            player.backpack.remove(self)
            self.kill()
            return True
        return False


def collide_hit_rect_with_rect(game_obj: GameObject,
                               sprite: pg.sprite.Sprite) -> bool:
    """Collide the hit_rect of a GameObject with the rect of a Sprite.
    """
    return game_obj.hit_rect.colliderect(sprite.rect)

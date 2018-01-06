from collections import namedtuple, Callable
from random import uniform

import pygame as pg
from pygame.math import Vector2

import attr
from pygame.sprite import Sprite
from pygame.transform import rotate

import images
from model import DynamicObject
from mods import ItemObject


class Projectile(DynamicObject):
    """A projectile fired from weapon. Projectile size is subclass dependent.
    """

    def __init__(self, pos: Vector2, direction: Vector2,
                 hits_player: bool = False) -> None:
        self._check_class_initialized()
        super().__init__(pos)
        if hits_player:
            groups_list = [self._groups.all_sprites,
                           self._groups.enemy_projectiles]
        else:
            groups_list = [self._groups.all_sprites, self._groups.bullets]
        pg.sprite.Sprite.__init__(self, groups_list)

        self._base_rect = self.image.get_rect().copy()

        assert direction.is_normalized()
        self.velocity = direction * self.speed * uniform(0.9, 1.1)
        self.spawn_time = self._timer.current_time

    def update(self) -> None:
        self.pos += self.velocity * self._timer.dt
        if pg.sprite.spritecollideany(self, self._groups.walls):
            self.kill()
        if self._lifetime_exceeded:
            self.kill()

    @property
    def rect(self) -> pg.Rect:
        self._base_rect.center = self.pos
        return self._base_rect

    @property
    def _lifetime_exceeded(self) -> bool:
        lifetime = self._timer.current_time - self.spawn_time
        return lifetime > self.max_lifetime

    @property
    def image(self) -> pg.Surface:
        raise NotImplementedError

    @property
    def max_lifetime(self) -> int:
        raise NotImplementedError

    @property
    def speed(self) -> int:
        raise NotImplementedError

    @property
    def damage(self) -> int:
        raise NotImplementedError


@attr.s
class ProjectileData(object):
    hits_player = attr.ib(type=bool)
    damage = attr.ib(type=int)
    speed = attr.ib(type=int)
    max_lifetime = attr.ib(type=int)
    image_file = attr.ib(type=str)
    angled_image = attr.ib(default=False, type=bool)
    rotating_image = attr.ib(default=False, type=bool)
    drops_on_kill = attr.ib(default=None, type=Callable)


class SimpleProjectile(Projectile):
    def __init__(self, pos: Vector2, direction: Vector2,
                 data: ProjectileData) -> None:
        self._data = data
        super().__init__(pos, direction, data.hits_player)

    @property
    def damage(self) -> int:
        return self._data.damage

    @property
    def image(self) -> pg.Surface:
        return images.get_image(self._data.image_file)

    @property
    def max_lifetime(self) -> int:
        return self._data.max_lifetime

    @property
    def speed(self) -> int:
        return self._data.speed


class FancyProjectile(SimpleProjectile):
    """A projectile with interesting effects."""

    def __init__(self, pos: Vector2, direction: Vector2,
                 data: ProjectileData) -> None:
        self._init_image(data, direction)
        self._init_kill_method(data.drops_on_kill)

        super().__init__(pos, direction, data)

    def _init_kill_method(self, constructor):
        if constructor is not None:
            self._kill_method = constructor
        else:
            self._kill_method = lambda x: None

    def _init_image(self, data, direction):
        self._base_image = images.get_image(data.image_file)
        if data.angled_image:
            angle = direction.angle_to(Vector2(0, 0))
            self._base_image = rotate(self._base_image, angle)
        if data.rotating_image:
            self._process_image = self._rotate_image
        else:
            self._process_image = lambda x: x

    def _rotate_image(self, image: pg.Surface) -> pg.Surface:
        angle = self._timer.current_time // 2 % 360
        return pg.transform.rotate(image, angle)

    @property
    def image(self):
        return self._process_image(self._base_image)

    def kill(self):
        super().kill()
        self._kill_method(self.pos)


class ProjectileFactory(object):
    def __init__(self, data: ProjectileData) -> None:
        self._data = data

    def build_projectile(self, pos: Vector2,
                         direction: Vector2) -> SimpleProjectile:
        projectile = FancyProjectile(pos, direction, self._data)

        return projectile

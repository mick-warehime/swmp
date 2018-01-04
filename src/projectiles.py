from collections import namedtuple
from random import uniform

import pygame as pg
from pygame.math import Vector2

import images
from model import DynamicObject


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
        self._vel = direction * self.speed * uniform(0.9, 1.1)
        self.spawn_time = self._timer.current_time

    def update(self) -> None:
        self.pos += self._vel * self._timer.dt
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


ProjectileData = namedtuple('ProjectileData', ('hits_player', 'damage',
                                               'speed', 'max_lifetime',
                                               'image_file'))


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


class ProjectileFactory(object):
    def __init__(self, data: ProjectileData) -> None:
        self._data = data

    def build_projectile(self, pos: Vector2,
                         direction: Vector2) -> SimpleProjectile:
        return SimpleProjectile(pos, direction, self._data)

from collections import namedtuple
from random import uniform

import pygame as pg
from pygame.math import Vector2

import attr
from pygame.sprite import Sprite
from pygame.transform import rotate

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
        projectile = SimpleProjectile(pos, direction, self._data)
        if self._data.angled_image:
            projectile = AngledProjectile(projectile)
        return projectile


class AngledProjectile(Projectile):
    """A projectile whose image is angled in a specific direction. """

    def __init__(self, base_projectile: Projectile):
        self._base_projectile = base_projectile

        direction = base_projectile.velocity.normalize()
        base_image = base_projectile.image
        angle = direction.angle_to(Vector2(0, 0))
        self._image = rotate(base_image, angle)

        super().__init__(base_projectile.pos, direction)
        self._replace_in_groups(base_projectile)

    def _replace_in_groups(self, base_projectile):
        # After the init call, the object is already put into specific
        # groups. We instead take it out of those groups, and put it in the
        # groups of the base_projectile, while removing the base_projectile.
        container_groups = self._groups.which_in(base_projectile)
        Sprite.kill(base_projectile)  # Remove base_projectile from Groups
        Sprite.kill(self)
        Sprite.__init__(self, container_groups)

    @property
    def image(self) -> pg.Surface:
        return self._image

    @property
    def speed(self) -> int:
        return self._base_projectile.speed

    @property
    def max_lifetime(self) -> int:
        return self._base_projectile.max_lifetime

        # def __getattr__(self, item):
        #     if item != 'image':
        #         return getattr(self._base_projectile, item)
        #     else:
        #         return self.image

    @property
    def damage(self) -> int:
        return self._base_projectile.damage

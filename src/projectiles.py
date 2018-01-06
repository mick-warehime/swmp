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


class RotatingProjectile(Projectile):
    """A projectile whose image is angled in a specific direction.

    This is a decorator pattern incorporating a base projectile. The
    direction is determined by the base projectile's velocity.

    In order to correctly angle the image the base projectile's image must be
    oriented facing 0 degrees.
    """

    def __init__(self, base_projectile: Projectile):
        self._base_projectile = base_projectile
        direction = base_projectile.velocity.normalize()
        self._image = base_projectile.image

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
        angle = self._timer.current_time // 2 % 360
        return pg.transform.rotate(self._image, angle)

    @property
    def speed(self) -> int:
        return self._base_projectile.speed

    @property
    def max_lifetime(self) -> int:
        return self._base_projectile.max_lifetime

    @property
    def damage(self) -> int:
        return self._base_projectile.damage


class AngledProjectile(Projectile):
    """A projectile whose image rotates over time.

    This is a decorator pattern incorporating a base projectile.
    """

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

    @property
    def damage(self) -> int:
        return self._base_projectile.damage


class DropsOnKill(Projectile):
    """A projectile that drops an ItemObject when its kill() method is called.

    This is a decorator pattern incorporating a base projectile.
    """

    def __init__(self, base_proj: Projectile, item_constructor: Callable):
        self._base_projectile = base_proj
        self._item_constructor = item_constructor

        direction = base_proj.velocity.normalize()
        super().__init__(base_proj.pos, direction)
        self._replace_in_groups(base_proj)

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
        return self._base_projectile.image

    @property
    def speed(self) -> int:
        return self._base_projectile.speed

    @property
    def max_lifetime(self) -> int:
        return self._base_projectile.max_lifetime

    @property
    def damage(self) -> int:
        return self._base_projectile.damage

    def kill(self):
        self._base_projectile.pos = self.pos
        self._base_projectile.kill()
        self._item_constructor(self.pos)
        super().kill()


class ProjectileFactory(object):
    def __init__(self, data: ProjectileData) -> None:
        self._data = data

    def build_projectile(self, pos: Vector2,
                         direction: Vector2) -> SimpleProjectile:
        projectile = SimpleProjectile(pos, direction, self._data)
        if self._data.angled_image:
            projectile = AngledProjectile(projectile)

        if self._data.rotating_image:
            projectile = RotatingProjectile(projectile)

        constructor = self._data.drops_on_kill
        if constructor is not None:
            projectile = DropsOnKill(projectile, constructor)
        return projectile

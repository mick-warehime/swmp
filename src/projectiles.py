from collections import namedtuple
from random import uniform, randint

import pygame as pg
from pygame.math import Vector2
from pygame.transform import rotate

import settings
from model import TimeAccess, GameObject
from view import images


class Projectile(GameObject, TimeAccess):
    """A projectile fired from weapon. Projectile size is subclass dependent.
    """

    def __init__(self, pos: Vector2, direction: Vector2,
                 hits_player: bool = False) -> None:
        super().__init__(pos)
        if hits_player:
            groups_list = [self.groups.all_sprites,
                           self.groups.enemy_projectiles]
        else:
            groups_list = [self.groups.all_sprites, self.groups.bullets]
        pg.sprite.Sprite.__init__(self, groups_list)

        self._base_rect = self.image.get_rect().copy()

        assert direction.is_normalized()
        self.velocity = direction * self.speed * uniform(0.9, 1.1)
        self.spawn_time = self.timer.current_time

    def update(self) -> None:
        self.pos += self.velocity * self.timer.dt
        if pg.sprite.spritecollideany(self, self.groups.walls):
            self.kill()
        if self._lifetime_exceeded:
            self.kill()

    @property
    def rect(self) -> pg.Rect:
        self._base_rect.center = self.pos
        return self._base_rect

    @property
    def _lifetime_exceeded(self) -> bool:
        lifetime = self.timer.current_time - self.spawn_time
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


BaseProjectileData = namedtuple('BaseProjectileData', ('hits_player',
                                                       'damage', 'speed',
                                                       'max_lifetime',
                                                       'image_file',
                                                       'angled_image',
                                                       'rotating_image',
                                                       'drops_on_kill'))


class ProjectileData(BaseProjectileData):
    def __new__(cls, hits_player: bool, damage: int, speed: int,
                max_lifetime: int, image_file: str,
                angled_image: bool = False, rotating_image: bool = False,
                drops_on_kill: str = None) -> BaseProjectileData:
        return super().__new__(cls, hits_player, damage, speed,
                               max_lifetime, image_file, angled_image,
                               rotating_image, drops_on_kill)


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

        super().__init__(pos, direction, data)

    def _init_image(self, data: ProjectileData,
                    direction: Vector2) -> None:
        self._base_image = images.get_image(data.image_file)
        if data.angled_image:
            angle = direction.angle_to(Vector2(0, 0))
            self._base_image = rotate(self._base_image, angle)
        if data.rotating_image:
            self._process_image = self._rotate_image
        else:
            self._process_image = lambda x: x

    def _rotate_image(self, image: pg.Surface) -> pg.Surface:
        angle = self.timer.current_time // 2 % 360
        return pg.transform.rotate(image, angle)

    @property
    def image(self) -> pg.Surface:
        return self._process_image(self._base_image)

    def kill(self) -> None:
        super().kill()
        if self._data.drops_on_kill is not None:
            from data.constructors import build_map_object
            build_map_object(self._data.drops_on_kill, self.pos)


class ProjectileFactory(object):
    def __init__(self, data: ProjectileData) -> None:
        self._data = data

    def build(self, pos: Vector2,
              direction: Vector2) -> SimpleProjectile:
        projectile = FancyProjectile(pos, direction, self._data)

        return projectile


class MuzzleFlash(GameObject, TimeAccess):
    def __init__(self, pos: Vector2) -> None:
        pg.sprite.Sprite.__init__(self, self.groups.all_sprites)
        super().__init__(pos)
        self._rect = self.image.get_rect().copy()
        self._rect.center = self.pos
        self._spawn_time = self.timer.current_time

    def update(self) -> None:
        if self._fade_out():
            self.kill()

    @property
    def image(self) -> pg.Surface:
        size = randint(20, 50)
        flash_img = images.get_muzzle_flash()
        return pg.transform.scale(flash_img, (size, size))

    def _fade_out(self) -> bool:
        time_elapsed = self.timer.current_time - self._spawn_time
        return time_elapsed > settings.FLASH_DURATION

    @property
    def rect(self) -> pg.Rect:
        return self._rect

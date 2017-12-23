import pygame as pg
from random import uniform, randint
from pygame.math import Vector2

from model import DynamicObject
import settings
import images


def initialize_classes() -> None:
    Bullet.initialize_class()


class Bullet(DynamicObject):
    """A projectile fired from weapon. Projectile size is subclass dependent.
    """
    class_initialized = False
    max_lifetime: int = 0
    speed: int = 0
    damage: int = 0
    small_base_image = None

    def __init__(self, pos: Vector2, direction: Vector2) -> None:
        self._check_class_initialized()
        groups_list = [self._groups.all_sprites, self._groups.bullets]
        pg.sprite.Sprite.__init__(self, groups_list)
        self.rect = self.image.get_rect()
        self.hit_rect = self.rect
        self.pos = Vector2(pos)
        self.rect.center = pos

        self._vel = direction * self.speed * uniform(0.9, 1.1)
        self.spawn_time = self._timer.current_time

    def update(self) -> None:
        self.pos += self._vel * self._timer.dt
        self.rect.center = self.pos
        if pg.sprite.spritecollideany(self, self._groups.walls):
            self.kill()
        if self._lifetime_exceeded:
            self.kill()

    @property
    def image(self) -> pg.Surface:
        raise NotImplementedError

    @property
    def _lifetime_exceeded(self) -> bool:
        lifetime = self._timer.current_time - self.spawn_time
        return lifetime > self.max_lifetime

    @classmethod
    def initialize_class(cls) -> None:
        cls._init_base_image(images.BULLET_IMG)
        cls.small_base_image = pg.transform.scale(cls.base_image, (10, 10))
        cls.class_initialized = True

    def _check_class_initialized(self) -> None:
        super(Bullet, self)._check_class_initialized()
        if not self.class_initialized:
            raise RuntimeError('Bullets class must be initialized before '
                               'instantiating a Bullet.')


class BigBullet(Bullet):
    """A large bullet coming out of a pistol."""
    max_lifetime = 1000
    speed = 500
    damage = 75

    @property
    def image(self) -> pg.Surface:
        return self.base_image


class LittleBullet(Bullet):
    """A small bullet coming out of a shotgun."""
    max_lifetime = 500
    speed = 400
    damage = 25

    @property
    def image(self) -> pg.Surface:
        return self.small_base_image


class MuzzleFlash(DynamicObject):
    def __init__(self, pos: Vector2) -> None:
        self._check_class_initialized()
        pg.sprite.Sprite.__init__(self, self._groups.all_sprites)
        size = randint(20, 50)

        flash_img = images.get_muzzle_flash()
        self.image = pg.transform.scale(flash_img, (size, size))

        self.rect = self.image.get_rect()
        self.pos = pos
        self.rect.center = pos
        self._spawn_time = self._timer.current_time

    def update(self) -> None:
        if self._fade_out():
            self.kill()

    def _fade_out(self) -> bool:
        time_elapsed = self._timer.current_time - self._spawn_time
        return time_elapsed > settings.FLASH_DURATION

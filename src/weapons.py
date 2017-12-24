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
    class_initialized = True
    max_lifetime: int = 0
    speed: int = 0
    damage: int = 0

    def __init__(self, pos: Vector2, direction: Vector2) -> None:
        self._check_class_initialized()
        super().__init__(pos)
        groups_list = [self._groups.all_sprites, self._groups.bullets]
        pg.sprite.Sprite.__init__(self, groups_list)

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
        return images.get_image(images.BULLET_IMG)


class LittleBullet(Bullet):
    """A small bullet coming out of a shotgun."""
    max_lifetime = 500
    speed = 400
    damage = 25
    _base_image = None

    @property
    def image(self) -> pg.Surface:
        if LittleBullet._base_image is None:
            bullet_img = images.get_image(images.BULLET_IMG)
            small_img = pg.transform.scale(bullet_img, (10, 10))
            LittleBullet._base_image = small_img
        return self._base_image


class MuzzleFlash(DynamicObject):
    def __init__(self, pos: Vector2) -> None:
        self._check_class_initialized()
        pg.sprite.Sprite.__init__(self, self._groups.all_sprites)
        super().__init__(pos)
        self._spawn_time = self._timer.current_time

    def update(self) -> None:
        if self._fade_out():
            self.kill()

    @property
    def image(self) -> pg.Surface:
        size = randint(20, 50)
        flash_img = images.get_muzzle_flash()
        return pg.transform.scale(flash_img, (size, size))

    def _fade_out(self) -> bool:
        time_elapsed = self._timer.current_time - self._spawn_time
        return time_elapsed > settings.FLASH_DURATION

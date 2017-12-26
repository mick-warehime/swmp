import pygame as pg
from random import uniform, randint
from pygame.math import Vector2

from model import DynamicObject
import settings
import images


class Projectile(DynamicObject):
    """A projectile fired from weapon. Projectile size is subclass dependent.
    """
    max_lifetime: int = 0
    speed: int = 0
    damage: int = 0

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

        assert direction.is_normalized()
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


class BigBullet(Projectile):
    """A large bullet coming out of a pistol."""
    max_lifetime = 1000
    speed = 400
    damage = 75

    @property
    def image(self) -> pg.Surface:
        return images.get_image(images.BULLET_IMG)


class LittleBullet(Projectile):
    """A small bullet coming out of a shotgun."""
    max_lifetime = 500
    speed = 500
    damage = 25
    _image = None

    @property
    def image(self) -> pg.Surface:
        if LittleBullet._image is None:
            bullet_img = images.get_image(images.BULLET_IMG)
            small_img = pg.transform.scale(bullet_img, (10, 10))
            LittleBullet._image = small_img
        return self._image


class EnemyVomit(Projectile):
    max_lifetime = 600
    speed = 300
    damage = 20

    def __init__(self, pos: Vector2, direction: Vector2) -> None:
        super().__init__(pos, direction, hits_player=True)

    @property
    def image(self) -> pg.Surface:
        return images.get_image(images.VOMIT)


class Rock(Projectile):
    max_lifetime = 800
    speed = 150
    damage = 25

    @property
    def image(self) -> pg.Surface:
        angle = self._timer.current_time % 360
        image = images.get_image(images.ROCK)
        return pg.transform.rotate(image, angle)


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

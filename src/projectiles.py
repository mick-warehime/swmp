from random import uniform

import pygame as pg
from pygame.math import Vector2

import images
from model import DynamicObject


class Projectile(DynamicObject):
    """A projectile fired from weapon. Projectile size is subclass dependent.
    """
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
    def image(self) -> pg.Surface:
        raise NotImplementedError

    @property
    def rect(self) -> pg.Rect:
        self._base_rect.center = self.pos
        return self._base_rect

    @property
    def _lifetime_exceeded(self) -> bool:
        lifetime = self._timer.current_time - self.spawn_time
        return lifetime > self.max_lifetime


class EnemyVomit(Projectile):
    max_lifetime = 600
    speed = 300
    damage = 20

    def __init__(self, pos: Vector2, direction: Vector2) -> None:
        super().__init__(pos, direction, hits_player=True)

    @property
    def image(self) -> pg.Surface:
        return images.get_image(images.VOMIT)

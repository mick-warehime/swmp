import pygame as pg
from random import uniform, randint
from pygame.math import Vector2
from model import Timer, Group, Groups
import settings
import sounds
import images


class Weapon(object):
    """Generates bullets or other sources of damage."""

    def __init__(self, label: str, timer: Timer, groups: Groups) -> None:
        self._label = ''
        self.set(label)
        self._timer = timer
        self._groups = groups
        self._last_shot = timer.current_time

    def set(self, label: str) -> None:
        if label not in settings.WEAPONS:
            raise ValueError('Weapon \'%s\' not defined in settings.py. '
                             'Allowed values: %s.'
                             % (label, settings.WEAPONS.keys()))
        self._label = label

    @property
    def shoot_rate(self) -> int:
        return settings.WEAPONS[self._label]['rate']

    @property
    def kick_back(self) -> int:
        return settings.WEAPONS[self._label]['kickback']

    @property
    def bullet_count(self) -> int:
        return settings.WEAPONS[self._label]['bullet_count']

    @property
    def spread(self) -> int:
        return settings.WEAPONS[self._label]['spread']

    def shoot(self, pos: Vector2, rot: Vector2) -> None:
        self._last_shot = self._timer.current_time
        direction = Vector2(1, 0).rotate(-rot)
        origin = pos + settings.BARREL_OFFSET.rotate(-rot)

        for _ in range(self.bullet_count):
            spread = uniform(-self.spread, self.spread)
            Bullet(self._timer, self._groups, origin,
                   direction.rotate(spread), self._label)
            sounds.fire_weapon_sound(self._label)
        MuzzleFlash(self._groups.all_sprites, origin)

    @property
    def can_shoot(self) -> bool:
        now = self._timer.current_time
        return now - self._last_shot > self.shoot_rate


class Bullet(pg.sprite.Sprite):
    def __init__(self, timer: Timer, groups: Groups, pos: Vector2,
                 direction: Vector2, weapon: str) -> None:
        groups_list = [groups.all_sprites, groups.bullets]
        pg.sprite.Sprite.__init__(self, groups_list)
        self._timer = timer
        self._walls = groups.walls
        self.weapon = weapon

        blt_img = images.get_image(images.BULLET_IMG)

        if weapon == 'pistol':
            self.image = blt_img
        else:
            self.image = pg.transform.scale(blt_img, (10, 10))
        self.rect = self.image.get_rect()
        self.hit_rect = self.rect
        self.pos = Vector2(pos)
        self.rect.center = pos

        speed = settings.WEAPONS[weapon]['bullet_speed']
        self._vel = direction * speed * uniform(0.9, 1.1)
        self.spawn_time = self._timer.current_time
        self.damage = settings.WEAPONS[weapon]['damage']

    def update(self) -> None:
        self.pos += self._vel * self._timer.dt
        self.rect.center = self.pos
        if pg.sprite.spritecollideany(self, self._walls):
            self.kill()
        if self._lifetime_exceeded():
            self.kill()

    def _lifetime_exceeded(self) -> bool:
        lifetime = self._timer.current_time - self.spawn_time
        max_time = settings.WEAPONS[self.weapon]['bullet_lifetime']
        return lifetime > max_time


class MuzzleFlash(pg.sprite.Sprite):
    def __init__(self, all_sprites: Group, pos: Vector2) -> None:
        pg.sprite.Sprite.__init__(self, all_sprites)
        size = randint(20, 50)

        flash_img = images.get_muzzle_flash()
        self.image = pg.transform.scale(flash_img, (size, size))

        self.rect = self.image.get_rect()
        self.pos = pos
        self.rect.center = pos
        self.spawn_time = pg.time.get_ticks()

    def update(self) -> None:
        if pg.time.get_ticks() - self.spawn_time > settings.FLASH_DURATION:
            self.kill()

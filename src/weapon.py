import pygame as pg
from random import uniform, randint
from pygame.math import Vector2
from model import Timer, Group, Groups, DynamicObject
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
            Bullet(origin, direction.rotate(spread), self._label)
            sounds.fire_weapon_sound(self._label)
        MuzzleFlash(self._groups.all_sprites, origin)

    @property
    def can_shoot(self) -> bool:
        now = self._timer.current_time
        return now - self._last_shot > self.shoot_rate


class Bullet(DynamicObject):
    class_initialized = False

    def __init__(self, pos: Vector2, direction: Vector2, weapon: str) -> None:
        self._check_class_initialized()
        groups_list = [self._groups.all_sprites, self._groups.bullets]
        pg.sprite.Sprite.__init__(self, groups_list)
        self._walls = self._groups.walls
        self.weapon = weapon

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

    @property
    def image(self) -> pg.Surface:
        assert self.weapon in ('pistol', 'shotgun')
        if self.weapon == 'pistol':
            return self.base_image
        else:
            return pg.transform.scale(self.base_image, (10, 10))

    @classmethod
    def initialize_class(cls) -> None:
        cls._init_base_image(images.BULLET_IMG)
        cls.class_initialized = True

    def _check_class_initialized(self) -> None:
        super(Bullet, self)._check_class_initialized()
        if not self.class_initialized:
            raise RuntimeError('Bullets class must be initialized before '
                               'instantiating a Bullet.')


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

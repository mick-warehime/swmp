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
        barrel_offset = pg.math.Vector2(30, 10)
        origin = pos + barrel_offset.rotate(-rot)

        make_bullet = BigBullet if self._label == 'pistol' else LittleBullet
        for _ in range(self.bullet_count):
            spread = uniform(-self.spread, self.spread)
            make_bullet(origin, direction.rotate(spread))
        sounds.fire_weapon_sound(self._label)
        MuzzleFlash(self._groups.all_sprites, origin)

    @property
    def can_shoot(self) -> bool:
        now = self._timer.current_time
        return now - self._last_shot > self.shoot_rate


class Bullet(DynamicObject):
    """A projectile fired from weapon. Projectile size is subclass dependent.
    """
    class_initialized = False
    max_lifetime = None
    speed = None
    damage = None
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
    max_lifetime = settings.WEAPONS['pistol']['bullet_lifetime']
    speed = settings.WEAPONS['pistol']['bullet_speed']
    damage = settings.WEAPONS['pistol']['damage']

    @property
    def image(self) -> pg.Surface:
        return self.base_image


class LittleBullet(Bullet):
    """A small bullet coming out of a shotgun."""
    max_lifetime = settings.WEAPONS['shotgun']['bullet_lifetime']
    speed = settings.WEAPONS['shotgun']['bullet_speed']
    damage = settings.WEAPONS['shotgun']['damage']

    @property
    def image(self) -> pg.Surface:
        return self.small_base_image


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

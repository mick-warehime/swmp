"""Module for defining Humanoid abilities."""
from random import uniform
from typing import Union, Callable

from pygame.math import Vector2

import sounds
from typing import Any

from model import Timer
from tilemap import ObjectType
from weapons import BigBullet, LittleBullet, MuzzleFlash, EnemyVomit


def initialize_classes(timer: Timer) -> None:
    CoolDownAbility.initialize_class(timer)


class Ability(object):
    """Abstract base class for a generic Humanoid ability."""
    class_initialized = True

    def use(self, humanoid: Any) -> None:
        raise NotImplementedError

    @property
    def can_use(self) -> bool:
        raise NotImplementedError

    @classmethod
    def _check_class_initialized(cls) -> None:
        if not cls.class_initialized:
            raise RuntimeError('Class %s must be initialized before '
                               'instantiating an object.' % (cls,))


class CoolDownAbility(Ability):
    _cool_down: Union[int, None] = None
    _timer: Union[None, Timer] = None
    class_initialized = False

    def __init__(self) -> None:
        self._check_class_initialized()
        self._update_last_use()

    @classmethod
    def initialize_class(cls, timer: Timer) -> None:
        cls._timer = timer
        cls.class_initialized = True

    @property
    def can_use(self) -> bool:
        now = self._timer.current_time
        return now - self._last_use > self._cool_down

    def use(self, humanoid: Any) -> None:
        raise NotImplementedError

    def _update_last_use(self) -> None:
        self._last_use = self._timer.current_time


class FireProjectile(CoolDownAbility):
    _kickback: Union[int, None] = None
    _spread: Union[int, None] = None
    _projectile_count: Union[None, int] = None
    _make_projectile: Union[None, Callable] = None

    def use(self, humanoid: Any) -> None:
        self._update_last_use()
        pos = humanoid.pos
        rot = humanoid.rot

        direction = Vector2(1, 0).rotate(-rot)
        barrel_offset = Vector2(30, 10)
        origin = pos + barrel_offset.rotate(-rot)

        for _ in range(self._projectile_count):
            spread = uniform(-self._spread, self._spread)
            self._make_projectile(origin, direction.rotate(spread))

        humanoid._vel = Vector2(-self._kickback, 0).rotate(-rot)
        self._fire_effects(origin)

    def _fire_effects(self, origin: Vector2) -> None:
        """Other effects that happen when used, such as making a sound or a
        muzzle flash."""
        raise NotImplementedError


class FirePistol(FireProjectile):
    _kickback = 200
    _cool_down = 250
    _spread = 5
    _projectile_count = 1
    _make_projectile = BigBullet

    def _fire_effects(self, origin: Vector2) -> None:
        sounds.fire_weapon_sound(ObjectType.PISTOL)
        MuzzleFlash(origin)


class SpewVomit(FireProjectile):
    _kickback = 0
    _cool_down = 250
    _spread = 5
    _projectile_count = 1
    _make_projectile = EnemyVomit

    def _fire_effects(self, origin: Vector2) -> None:
        sounds.spew_vomit_sound()


class FireShotgun(FireProjectile):
    _kickback = 300
    _cool_down = 900
    _spread = 20
    _projectile_count = 12
    _make_projectile = LittleBullet

    def _fire_effects(self, origin: Vector2) -> None:
        sounds.fire_weapon_sound(ObjectType.SHOTGUN)
        MuzzleFlash(origin)


class Heal(CoolDownAbility):
    """A healing ability with a timed cooldown and finite use count."""
    _cool_down: Union[int, None] = 300

    def __init__(self, num_uses: int, heal_amount: int) -> None:
        super().__init__()
        self.uses_left = num_uses
        self._heal_amount = heal_amount

    @property
    def can_use(self) -> bool:
        can_use = super().can_use
        can_use = can_use and self.uses_left > 0
        return can_use

    def use(self, humanoid: Any) -> None:
        if humanoid.damaged:
            self._update_last_use()
            self.uses_left -= 1
            sounds.play(sounds.HEALTH_UP)
            humanoid.increment_health(self._heal_amount)

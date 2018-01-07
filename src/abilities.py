"""Module for defining Humanoid abilities."""
from random import uniform
from typing import Any
from typing import Union, Callable

import attr
from pygame.math import Vector2

import sounds
from model import Timer, EnergySource
from projectiles import ProjectileData


def initialize_classes(timer: Timer) -> None:
    Ability.initialize_class(timer)


class Ability(object):
    _cool_down_time: Union[int, None] = None
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
        return self._time_since_last_use > self._cool_down_time

    @property
    def _time_since_last_use(self) -> int:
        return self._timer.current_time - self._last_use

    @property
    def cooldown_fraction(self) -> float:
        fraction = float(self._time_since_last_use) / self._cool_down_time

        return min(max(0.0, fraction), 1.0)

    def use(self, humanoid: Any) -> None:
        raise NotImplementedError

    def _update_last_use(self) -> None:
        self._last_use = self._timer.current_time

    @classmethod
    def _check_class_initialized(cls) -> None:
        if not cls.class_initialized:
            raise RuntimeError('Class %s must be initialized before '
                               'instantiating an object.' % (cls,))


@attr.s
class AbilityData(object):
    cool_down_time: int = attr.ib()
    energy_required: int = attr.ib(default=0)
    heal_amount: int = attr.ib(default=0)
    projectile_ability_data: ProjectileAbilityData = attr.ib(default=None)


@attr.s
class ProjectileAbilityData(object):
    projectile_data: ProjectileData = attr.ib()
    projectile_count: int = attr.ib(default=1)
    kickback: int = attr.ib(default=0)
    spread: int = attr.ib(default=0)


class EnergyAbility(Ability):
    """Ability that can only activate by expending an energy source.

    This uses the `decorator' (?) pattern to add an energy requirement to a
    base ability.

    Note: In order for this class to work correctly, the base ability's `use'
    method must always implement the ability (unlike the Heal ability,
    which only implements it if the humanoid is damaged).
    """

    def __init__(self, base_ability: Ability, energy_required: float) -> None:
        super().__init__()
        self._base_ability = base_ability
        self._energy_source: EnergySource = None
        self.energy_required = energy_required

    def use(self, humanoid: Any) -> None:
        assert self.can_use
        self._base_ability.use(humanoid)
        self._energy_source.expend_energy(self.energy_required)

    def assign_energy_source(self, source: EnergySource) -> None:
        self._energy_source = source

    @property
    def can_use(self) -> bool:
        if self._energy_source is None:
            raise RuntimeError('An energy source must be assigned before '
                               '.can_use is defined.')
        if self.energy_required > self._energy_source.energy_available:
            return False
        return self._base_ability.can_use

    @property
    def cooldown_fraction(self) -> float:
        return self._base_ability.cooldown_fraction


class FireProjectile(Ability):
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


class Heal(Ability):
    """A healing ability with a timed cooldown and finite use count."""
    _cool_down_time: Union[int, None] = 300

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

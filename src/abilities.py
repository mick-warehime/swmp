"""Module for defining Humanoid abilities."""
from random import uniform
from typing import Any
from typing import Union, Callable

import attr
from pygame.math import Vector2

from model import Timer, EnergySource
from projectiles import ProjectileData, ProjectileFactory

EffectFun = Callable[[Vector2], None]


def initialize_classes(timer: Timer) -> None:
    Ability.initialize_class(timer)


def null_effect(origin: Vector2) -> None:
    pass


def null_use(humanoid: Any) -> None:
    raise UserWarning(
        'Null use function should not be called by Ability. Did you replace '
        'self._use_fun?')
    pass


class Ability(object):
    _cool_down_time: int = None
    _timer: Union[None, Timer] = None
    _use_fun: Callable[[Any], None] = null_use
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
    def cooldown_fraction(self) -> float:
        fraction = float(self._time_since_last_use) / self._cool_down_time

        return min(max(0.0, fraction), 1.0)

    def use(self, humanoid: Any) -> None:
        self._use_fun(humanoid)

    def _update_last_use(self) -> None:
        self._last_use = self._timer.current_time

    @property
    def _time_since_last_use(self) -> int:
        return self._timer.current_time - self._last_use

    @classmethod
    def _check_class_initialized(cls) -> None:
        if not cls.class_initialized:
            raise RuntimeError('Class %s must be initialized before '
                               'instantiating an object.' % (cls,))


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


class FireProjectileBase(Ability):
    _kickback: int = None
    _spread: int = None
    _projectile_count: int = None
    _fire_effect_fun: Callable[[Vector2], None] = None
    _make_projectile: Callable[[Vector2, Vector2], None] = None

    def __init__(self):
        super().__init__()
        self._use_fun = self._fire_projectile

    def _fire_projectile(self, humanoid: Any) -> None:
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
        self._fire_effect_fun(origin)


@attr.s
class AbilityData(object):
    cool_down_time: int = attr.ib()
    finite_uses: bool = attr.ib(default=False)
    uses_left: int = attr.ib(default=0)


@attr.s
class RegenerationAbilityData(object):
    heal_amount: int = attr.ib(default=0)


@attr.s
class ProjectileAbilityData(AbilityData):
    projectile_data: ProjectileData = attr.ib(default=None)
    kickback: int = attr.ib(default=0)
    spread: int = attr.ib(default=0)
    projectile_count: int = attr.ib(default=1)
    fire_effect: Callable[[Vector2], None] = attr.ib(default=null_effect)


# @attr.s
# class AbilityData(object):
#     cool_down_time: int = attr.ib()
#     # heal_amount: int = attr.ib(default=0)
#     projectile_ability_data: ProjectileAbilityData = attr.ib(default=None)
#     # energy_required: int = attr.ib(default=0)


# class DataAbility(Ability):
#     def __init__(self, data: AbilityData):
#         super().__init__()
#         self._cool_down_time = data.cool_down_time
#
#     def use(self, humanoid: Any) -> None:
#         pass

def combine_effect_funs(first_fun: EffectFun,
                        second_fun: EffectFun) -> EffectFun:
    """Return an EffectFun that calls two EffectFuns."""

    def combined_fun(origin: Vector2) -> None:
        first_fun(origin)
        second_fun(origin)

    return combined_fun


class FireProjectile(FireProjectileBase):
    def __init__(self, data: ProjectileAbilityData) -> None:
        self._cool_down_time = data.cool_down_time
        super().__init__()
        self._kickback = data.kickback
        self._spread = data.spread
        self._projectile_count = data.projectile_count

        factory = ProjectileFactory(data.projectile_data)
        self._make_projectile = factory.build_projectile
        self._fire_effect_fun = data.fire_effect

        if data.finite_uses:
            self.uses_left = data.uses_left
            self._fire_effect_fun = combine_effect_funs(data.fire_effect,
                                                        self.decrement_uses)

    def decrement_uses(self, origin: Vector2) -> None:
        self.uses_left -= 1

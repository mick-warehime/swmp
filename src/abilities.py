"""Module for defining Humanoid abilities."""
from random import uniform
from typing import Any, List
from typing import Union, Callable

import attr
from pygame.math import Vector2

import sounds
from model import Timer, EnergySource
from projectiles import ProjectileData, ProjectileFactory

EffectFun = Callable[[Vector2], None]
UseFun = Callable[[Any], None]


def initialize_classes(timer: Timer) -> None:
    Ability.initialize_class(timer)


def null_effect(origin: Vector2) -> None:
    pass


class Ability(object):
    _cool_down_time: int = None
    _timer: Union[None, Timer] = None
    class_initialized = False

    def __init__(self) -> None:
        self._check_class_initialized()
        self._update_last_use()
        self._use_funs: List[Callable[[Any], None]] = []

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
        for use_fun in self._use_funs:
            use_fun(humanoid)
        self._update_last_use()

    def _decrement_uses(self, *dummy_args: List[Any]) -> None:
        self.uses_left -= 1

    def _add_use_fun(self, fun: UseFun):
        self._use_funs.append(fun)

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
    """Ability that can only activate by modifying an energy source's reserves.

    This uses the `decorator' (?) pattern to add an energy requirement to a
    base ability.
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
        source = self._energy_source
        if source is None:
            raise RuntimeError('An energy source must be assigned before '
                               '.can_use is defined.')
        if self.energy_required > source.energy_available:
            return False
        return self._base_ability.can_use

    @property
    def cooldown_fraction(self) -> float:
        return self._base_ability.cooldown_fraction

    @property
    def uses_left(self):
        assert hasattr(self._base_ability, 'uses_left'), \
            'Ability %s is not finite use.' % (self._base_ability,)
        return self._base_ability.uses_left


@attr.s
class RegenerationAbilityData(object):
    cool_down_time: int = attr.ib()
    heal_amount: int = attr.ib(default=0)
    recharge_amount: int = attr.ib(default=0)
    finite_uses: bool = attr.ib(default=False)
    uses_left: int = attr.ib(default=0)


class RegenerationAbility(Ability):
    def __init__(self, data: RegenerationAbilityData):
        super().__init__()
        self._cool_down_time = data.cool_down_time

        assert data.heal_amount > 0 or data.recharge_amount > 0

        self._heal_amount = data.heal_amount
        self._recharge_amount = data.recharge_amount
        self._just_used = False

        if data.heal_amount > 0:
            self._add_use_fun(self._heal)

        if data.recharge_amount > 0:
            self._add_use_fun(self._recharge)

        if data.finite_uses:
            self.uses_left = data.uses_left
            self._add_use_fun(self._decrement_uses_just_used)

    def _decrement_uses_just_used(self, *dummy_args: List[Any]) -> None:

        if self._just_used:
            self._decrement_uses(*dummy_args)
            self._just_used = False

    def _heal(self, humanoid: Any) -> None:
        if humanoid.damaged:
            sounds.play(sounds.HEALTH_UP)
            humanoid.increment_health(self._heal_amount)
            self._just_used = True

    def _recharge(self, humanoid: Any) -> None:
        assert hasattr(humanoid, 'energy_source'), 'No energy source for %s' \
                                                   % (humanoid,)
        energy_source = humanoid.energy_source
        if energy_source.energy_available < energy_source.max_energy:
            energy_source.increment_energy(self._recharge_amount)
            sounds.play(sounds.HEALTH_UP)
            self._just_used = True


@attr.s
class ProjectileAbilityData(object):
    cool_down_time: int = attr.ib()
    projectile_data: ProjectileData = attr.ib()
    kickback: int = attr.ib(default=0)
    spread: int = attr.ib(default=0)
    projectile_count: int = attr.ib(default=1)
    fire_effect: Callable[[Vector2], None] = attr.ib(default=null_effect)
    finite_uses: bool = attr.ib(default=False)
    uses_left: int = attr.ib(default=0)


class FireProjectileBase(Ability):
    _kickback: int = None
    _spread: int = None
    _projectile_count: int = None
    _fire_effect_fun: Callable[[Vector2], None] = None
    _make_projectile: Callable[[Vector2, Vector2], None] = None

    def __init__(self):
        super().__init__()
        self._add_use_fun(self._fire_projectile)

    def _fire_projectile(self, humanoid: Any) -> None:
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
            self._add_use_fun(self._decrement_uses)

"""Module for defining Humanoid abilities."""

from random import uniform
from typing import Any, List
from typing import Union, Callable

from pygame.math import Vector2

import sounds
from data.projectiles_io import load_projectile_data
from model import Timer
from projectiles import ProjectileData, ProjectileFactory

UseFun = Callable[[Any], None]
CanUseFun = Callable[[Any], bool]


def initialize_classes(timer: Timer) -> None:
    Ability.initialize_class(timer)
    # AbilityFromData.initialize_class(timer)


INFINITE_USES = -1000


class Ability(object):
    _cool_down_time: int = None
    _timer: Union[None, Timer] = None
    class_initialized = False

    def __init__(self) -> None:
        self._check_class_initialized()

        self._use_funs: List[UseFun] = []
        self._can_use_funs: List[CanUseFun] = []

        cool_down = CooldownCondition(self._timer, self._cool_down_time)
        self.add_can_use_fun(cool_down.check)
        self.add_use_fun(cool_down.update_last_use)
        self._cool_down_fraction_fun = cool_down.cooldown_fraction

        self.uses_left = INFINITE_USES

    @classmethod
    def initialize_class(cls, timer: Timer) -> None:
        cls._timer = timer
        cls.class_initialized = True

    def can_use(self, humanoid: Any) -> bool:
        for condition in self._can_use_funs:
            if not condition(humanoid):
                return False
        return True

    def add_can_use_fun(self, can_use_fun: CanUseFun) -> None:
        self._can_use_funs.append(can_use_fun)

    @property
    def cooldown_fraction(self) -> float:
        return self._cool_down_fraction_fun()

    def use(self, humanoid: Any) -> None:
        for use_fun in self._use_funs:
            use_fun(humanoid)

    def add_use_fun(self, fun: UseFun) -> None:
        self._use_funs.append(fun)

    @classmethod
    def _check_class_initialized(cls) -> None:
        if not cls.class_initialized:
            raise RuntimeError('Class %s must be initialized before '
                               'instantiating an object.' % (cls,))


class AbilityData(object):
    def __init__(self, cool_down_time: int, finite_uses: bool = False,
                 uses_left: int = 0, energy_required: int = 0,
                 sound_on_use: str = None) -> None:
        self.cool_down_time = cool_down_time
        self.finite_uses = finite_uses
        self.uses_left = uses_left
        self.energy_required = energy_required
        self.sound_on_use = sound_on_use

    def __eq__(self, other: Any) -> bool:
        if not isinstance(self, type(other)):
            return False
        if self.cool_down_time != other.cool_down_time:
            return False
        if self.finite_uses != other.finite_uses:
            return False
        if self.energy_required != other.energy_required:
            return False
        if self.sound_on_use != other.sound_on_use:
            return False
        return True


class RegenerationAbilityData(AbilityData):
    def __init__(self, cool_down_time: int, heal_amount: int = 0,
                 recharge_amount: int = 0, finite_uses: bool = False,
                 uses_left: int = 0, energy_required: int = 0,
                 sound_on_use: str = None) -> None:
        super().__init__(cool_down_time, finite_uses, uses_left,
                         energy_required, sound_on_use)
        self.heal_amount = heal_amount
        self.recharge_amount = recharge_amount

    def __eq__(self, other: Any) -> bool:
        if not super().__eq__(other):
            return False

        if self.heal_amount != other.heal_amount:
            return False
        if self.recharge_amount != other.recharge_amount:
            return False

        return True


class ProjectileAbilityData(AbilityData):
    def __init__(self, cool_down_time: int,
                 projectile_data: ProjectileData = None,
                 finite_uses: bool = False, uses_left: int = 0,
                 energy_required: int = 0,
                 kickback: int = 0, spread: int = 0,
                 projectile_count: int = 1,
                 projectile_label: str = None,
                 sound_on_use: str = None) -> None:
        super().__init__(cool_down_time, finite_uses, uses_left,
                         energy_required, sound_on_use)
        if projectile_data is None:
            projectile_data = load_projectile_data(projectile_label)
        self.projectile_data = projectile_data
        self.kickback = kickback
        self.spread = spread
        self.projectile_count = projectile_count

    def __eq__(self, other: Any) -> bool:
        if not super().__eq__(other):
            return False

        if self.projectile_data != other.projectile_data:
            return False
        if self.kickback != other.kickback:
            return False
        if self.spread != other.spread:
            return False
        if self.projectile_count != other.projectile_count:
            return False

        return True


class GenericAbility(Ability):
    def __init__(self, data: AbilityData):
        self._cool_down_time = data.cool_down_time
        super().__init__()

        if data.energy_required > 0:
            condition = EnergyAvailable(data.energy_required)
            effect = ExpendEnergy(data.energy_required)
            self.add_use_fun(effect.activate)
            self.add_can_use_fun(condition.check)

        self.finite_uses = data.finite_uses
        if data.finite_uses:
            self.uses_left = data.uses_left
            effect = DecrementUses(self)
            self.add_use_fun(effect.activate)

        if data.sound_on_use is not None:
            effect = PlaySound(data.sound_on_use)
            self.add_use_fun(effect.activate)

        if hasattr(data, 'heal_amount'):
            self._load_regeneration_options(data)

        if hasattr(data, 'projectile_data'):
            self._load_projectile_options(data)

    def _load_regeneration_options(self, data: AbilityData) -> None:
        if data.heal_amount > 0 and data.recharge_amount > 0:
            condition = IsDamaged() or EnergyNotFull()
            heal = Heal(data.heal_amount)
            recharge = Recharge(data.recharge_amount)
            self.add_can_use_fun(condition.check)
            self.add_use_fun(heal.activate)
            self.add_use_fun(recharge.activate)
        elif data.heal_amount > 0:
            condition = IsDamaged()
            heal = Heal(data.heal_amount)
            self.add_can_use_fun(condition.check)
            self.add_use_fun(heal.activate)
        elif data.recharge_amount > 0:
            condition = EnergyNotFull()
            recharge = Recharge(data.recharge_amount)
            self.add_can_use_fun(condition.check)
            self.add_use_fun(recharge.activate)

    def _load_projectile_options(self, data: AbilityData):
        if data.kickback:
            effect = Kickback(data.kickback)
            self.add_use_fun(effect.activate)

        if data.projectile_data is not None:
            effect = MakeProjectile(data.projectile_data, data.spread,
                                    data.projectile_count)
            self.add_use_fun(effect.activate)


class Condition(object):
    """Evaluates a boolean function on a Humanoid."""

    def check(self, humanoid: Any) -> bool:
        raise NotImplementedError

    def __or__(self, other) -> object:
        assert isinstance(other, Condition)
        return _Or(self, other)


class _Or(Condition):
    def __init__(self, cond_0: Condition, cond_1: Condition) -> None:
        self._cond_0 = cond_0
        self._cond_1 = cond_1

    def check(self, humanoid: Any) -> bool:
        return self._cond_0.check(humanoid) or self._cond_1.check(humanoid)


class CooldownCondition(Condition):
    def __init__(self, timer: Timer, cool_down_time: int):
        self._timer = timer
        assert cool_down_time is not None
        self._cool_down_time = cool_down_time
        self._last_use = self._timer.current_time

    @property
    def _time_since_last_use(self) -> int:
        return self._timer.current_time - self._last_use

    def check(self, humanoid: Any) -> bool:
        return self._time_since_last_use > self._cool_down_time

    def update_last_use(self, humanoid: Any) -> None:
        self._last_use = self._timer.current_time

    def cooldown_fraction(self) -> float:
        fraction = float(self._time_since_last_use) / self._cool_down_time
        return min(max(0.0, fraction), 1.0)


class EnergyAvailable(Condition):
    def __init__(self, energy_required: int):
        self._energy_required = energy_required

    def check(self, humanoid: Any) -> bool:
        return self._energy_required < humanoid.energy_source.energy_available


class IsDamaged(Condition):
    def check(self, humanoid: Any) -> bool:
        return humanoid.damaged


class EnergyNotFull(Condition):
    def check(self, humanoid: Any) -> bool:
        source = humanoid.energy_source
        return source.energy_available < source.max_energy


class Effect(object):
    """Implements an effect on a Humanoid."""

    def activate(self, humanoid: Any) -> None:
        raise NotImplementedError


class Heal(Effect):
    def __init__(self, heal_amount: int) -> None:
        self._heal_amount = heal_amount

    def activate(self, humanoid: Any) -> None:
        humanoid.increment_health(self._heal_amount)


class Recharge(Effect):
    def __init__(self, recharge_amount: int) -> None:
        self._recharge_amount = recharge_amount

    def activate(self, humanoid: Any) -> None:
        humanoid.energy_source.increment_energy(self._recharge_amount)


class ExpendEnergy(Effect):
    def __init__(self, energy_required: int):
        self._energy_required = energy_required

    def activate(self, humanoid: Any) -> None:
        assert hasattr(humanoid, 'energy_source')
        humanoid.energy_source.expend_energy(self._energy_required)


class DecrementUses(Effect):
    def __init__(self, ability: Ability) -> None:
        self._used_ability = ability

    def activate(self, humanoid: Any) -> None:
        self._used_ability.uses_left -= 1


class PlaySound(Effect):
    def __init__(self, sound_file: str):
        self._sound_file = sound_file

    def activate(self, humanoid: Any) -> None:
        sounds.play(self._sound_file)


class Kickback(Effect):
    def __init__(self, kickback: int) -> None:
        self._kickback = kickback

    def activate(self, humanoid: Any) -> None:
        humanoid._vel = Vector2(-self._kickback, 0).rotate(-humanoid.rot)


class MakeProjectile(Effect):
    def __init__(self, projectile_data: ProjectileData, spread: int,
                 projectile_count: int):
        self._factory = ProjectileFactory(projectile_data)
        self._spread = spread
        self._count = projectile_count

    def activate(self, humanoid: Any) -> None:
        pos = humanoid.pos
        rot = humanoid.rot

        direction = Vector2(1, 0).rotate(-rot)
        barrel_offset = Vector2(30, 10)
        origin = pos + barrel_offset.rotate(-rot)

        for _ in range(self._count):
            spread = uniform(-self._spread, self._spread)
            self._factory.build(origin, direction.rotate(spread))

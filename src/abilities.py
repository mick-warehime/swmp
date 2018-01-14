"""Module for defining Humanoid abilities."""

from random import uniform
from typing import Any, List, Sequence
from typing import Union, Callable

from pygame.math import Vector2

import sounds
from data.projectiles_io import load_projectile_data
from model import Timer, EnergySource
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


class RegenerationAbility(Ability):
    def __init__(self, data: RegenerationAbilityData) -> None:
        self._cool_down_time = data.cool_down_time
        super().__init__()

        assert data.heal_amount > 0 or data.recharge_amount > 0

        if data.heal_amount > 0 and data.recharge_amount > 0:
            condition = IsDamagedOrEnergyNotFull()
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
        else:
            assert data.recharge_amount > 0
            condition = EnergyNotFull()
            recharge = Recharge(data.recharge_amount)
            self.add_can_use_fun(condition.check)
            self.add_use_fun(recharge.activate)

        self.finite_uses = data.finite_uses
        if data.finite_uses:
            self.uses_left = data.uses_left
            effect = DecrementUses(self)
            self.add_use_fun(effect.activate)

        if data.sound_on_use is not None:
            effect = PlaySound(data.sound_on_use)
            self.add_use_fun(effect.activate)


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


class FireProjectile(Ability):
    def __init__(self, data: ProjectileAbilityData) -> None:
        self._cool_down_time = data.cool_down_time
        super().__init__()

        if data.kickback:
            self._kickback = data.kickback
            self.add_use_fun(self._apply_kickback)

        self._spread = data.spread
        self._projectile_count = data.projectile_count

        factory = ProjectileFactory(data.projectile_data)
        self._make_projectile: Callable[[Vector2, Vector2], None] = \
            factory.build_projectile
        self.add_use_fun(self._fire_projectile)

        self.finite_uses = data.finite_uses
        if data.finite_uses:
            self.uses_left = data.uses_left
            effect = DecrementUses(self)
            self.add_use_fun(effect.activate)

        if data.sound_on_use is not None:
            effect = PlaySound(data.sound_on_use)
            self.add_use_fun(effect.activate)

        if data.energy_required > 0:
            condition = EnergyAvailable(data.energy_required)
            effect = ExpendEnergy(data.energy_required)
            self.add_use_fun(effect.activate)
            self.add_can_use_fun(condition.check)

    def _fire_projectile(self, humanoid: Any) -> None:
        assert self._make_projectile is not None, 'self._make_projectile ' \
                                                  'not defined.'
        pos = humanoid.pos
        rot = humanoid.rot

        direction = Vector2(1, 0).rotate(-rot)
        barrel_offset = Vector2(30, 10)
        origin = pos + barrel_offset.rotate(-rot)

        for _ in range(self._projectile_count):
            spread = uniform(-self._spread, self._spread)
            self._make_projectile(origin, direction.rotate(spread))

    def _apply_kickback(self, humanoid: Any) -> None:
        humanoid._vel = Vector2(-self._kickback, 0).rotate(-humanoid.rot)


class AbilityFactory(object):
    """Uses data to construct abilities."""

    def __init__(self, data: AbilityData) -> None:
        self._data = data

    def build(self) -> Ability:

        # TODO(dvirk): make an Enum for ability types?
        if isinstance(self._data, RegenerationAbilityData):
            ability = RegenerationAbility(self._data)  # type: ignore

        elif isinstance(self._data, ProjectileAbilityData):
            ability = FireProjectile(self._data)  # type: ignore

        return ability


class Condition(object):
    """Evaluates a boolean function on a Humanoid."""

    def check(self, humanoid: Any) -> bool:
        raise NotImplementedError


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


class IsDamagedOrEnergyNotFull(Condition):
    def __init__(self):
        self._is_damaged = IsDamaged()
        self._energy_not_full = EnergyNotFull()

    def check(self, humanoid: Any) -> bool:
        return self._energy_not_full(humanoid) or self._is_damaged(humanoid)


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

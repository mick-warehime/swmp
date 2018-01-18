"""Module for defining Humanoid abilities."""
from collections import namedtuple
from random import uniform
from typing import Any, List, Union

from pygame.math import Vector2

import sounds
from data.projectiles_io import load_projectile_data
from model import Timer
from projectiles import ProjectileData, ProjectileFactory, MuzzleFlash


def initialize_classes(timer: Timer) -> None:
    Ability.initialize_class(timer)
    # AbilityFromData.initialize_class(timer)


class Condition(object):
    """Evaluates a boolean function on a Humanoid."""

    def check(self, humanoid: Any) -> bool:
        raise NotImplementedError

    def __or__(self, other: Any) -> object:
        assert isinstance(other, Condition)
        return _Or(self, other)


class _Or(Condition):
    def __init__(self, cond_0: Condition, cond_1: Condition) -> None:
        self._cond_0 = cond_0
        self._cond_1 = cond_1

    def check(self, humanoid: Any) -> bool:
        return self._cond_0.check(humanoid) or self._cond_1.check(humanoid)


class Effect(object):
    """Implements an effect on a Humanoid."""

    def activate(self, humanoid: Any) -> None:
        raise NotImplementedError


class Ability(object):
    _timer: Union[None, Timer] = None
    class_initialized = False

    def __init__(self) -> None:
        self._check_class_initialized()

        self._use_effects: List[Effect] = []
        self._use_conditions: List[Condition] = []

        self.uses_left = 0

    @classmethod
    def initialize_class(cls, timer: Timer) -> None:
        cls._timer = timer
        cls.class_initialized = True

    def can_use(self, humanoid: Any) -> bool:
        for condition in self._use_conditions:
            if not condition.check(humanoid):
                return False
        return True

    def add_use_condition(self, condition: Condition) -> None:
        self._use_conditions.append(condition)

    @property
    def cooldown_fraction(self) -> float:
        raise NotImplementedError

    def use(self, humanoid: Any) -> None:
        for effect in self._use_effects:
            effect.activate(humanoid)

    def add_use_effect(self, effect: Effect) -> None:
        self._use_effects.append(effect)

    @classmethod
    def _check_class_initialized(cls) -> None:
        if not cls.class_initialized:
            raise RuntimeError('Class %s must be initialized before '
                               'instantiating an object.' % (cls,))


BaseAbilityData = namedtuple('BaseAbilityData',
                             ('cool_down_time', 'finite_uses', 'uses_left',
                              'energy_required', 'sound_on_use', 'kickback',
                              'spread', 'projectile_count',
                              'projectile_data', 'muzzle_flash',
                              'heal_amount', 'recharge_amount'))


class AbilityData(BaseAbilityData):
    def __new__(cls, cool_down_time: int, finite_uses: bool = False,
                uses_left: int = 0, energy_required: int = 0,
                sound_on_use: str = None, kickback: int = 0, spread: int = 0,
                projectile_count: int = 1, projectile_label: str = None,
                muzzle_flash: bool = False, heal_amount: int = 0,
                recharge_amount: int = 0) -> BaseAbilityData:

        if projectile_label is not None:
            projectile_data = load_projectile_data(projectile_label)
        else:
            projectile_data = None
        return super().__new__(cls, cool_down_time, finite_uses, uses_left,
                               energy_required, sound_on_use, kickback, spread,
                               projectile_count, projectile_data,
                               muzzle_flash, heal_amount, recharge_amount)

    def __eq__(self, other: Any) -> bool:
        if not isinstance(other, AbilityData):
            return False
        for field in self._fields:
            # Uses left should not determine equality.
            if field == 'uses_left':
                continue
            if getattr(self, field) != getattr(other, field):
                return False
        return True


class GenericAbility(Ability):
    def __init__(self, data: AbilityData) -> None:
        super().__init__()

        cool_down = CooldownCondition(self._timer, data.cool_down_time)
        update_use = UpdateLastUse(cool_down)
        self.add_use_condition(cool_down)
        self.add_use_effect(update_use)
        self._cool_down_fraction_fun = cool_down.cooldown_fraction

        if data.energy_required > 0:
            condition = EnergyAvailable(data.energy_required)
            effect: Effect = ExpendEnergy(data.energy_required)
            self.add_use_effect(effect)
            self.add_use_condition(condition)

        self.finite_uses = data.finite_uses
        if data.finite_uses:
            self.uses_left = data.uses_left
            effect = DecrementUses(self)
            self.add_use_effect(effect)

        if data.sound_on_use is not None:
            effect = PlaySound(data.sound_on_use)
            self.add_use_effect(effect)

        self._load_regeneration_options(data)

        self._load_projectile_options(data)

    @property
    def cooldown_fraction(self) -> float:
        return self._cool_down_fraction_fun()

    def _load_regeneration_options(self, data: AbilityData) -> None:
        if data.heal_amount > 0 and data.recharge_amount > 0:
            condition = IsDamaged() or EnergyNotFull()
            heal: Effect = Heal(data.heal_amount)
            recharge: Effect = Recharge(data.recharge_amount)
            self.add_use_condition(condition)
            self.add_use_effect(heal)
            self.add_use_effect(recharge)
        elif data.heal_amount > 0:
            condition = IsDamaged()
            heal = Heal(data.heal_amount)
            self.add_use_condition(condition)
            self.add_use_effect(heal)
        elif data.recharge_amount > 0:
            condition = EnergyNotFull()
            recharge = Recharge(data.recharge_amount)
            self.add_use_condition(condition)
            self.add_use_effect(recharge)

    def _load_projectile_options(self, data: AbilityData) -> None:
        if data.kickback:
            self.add_use_effect(Kickback(data.kickback))

        if data.projectile_data is not None:
            effect = MakeProjectile(data.projectile_data, data.spread,
                                    data.projectile_count)
            self.add_use_effect(effect)
        if data.muzzle_flash:
            self.add_use_effect(MuzzleFlashEffect())


class CooldownCondition(Condition):
    def __init__(self, timer: Timer, cool_down_time: int) -> None:
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
    def __init__(self, energy_required: int) -> None:
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


class UpdateLastUse(Effect):
    def __init__(self, cool_down_condition: CooldownCondition) -> None:
        self._cool_down_condition = cool_down_condition

    def activate(self, humanoid: Any) -> None:
        self._cool_down_condition.update_last_use(humanoid)


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
    def __init__(self, energy_required: int) -> None:
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
    def __init__(self, sound_file: str) -> None:
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
                 projectile_count: int) -> None:
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


class MuzzleFlashEffect(Effect):
    def activate(self, humanoid: Any) -> None:
        direction = humanoid.direction
        direction = direction.rotate(20)
        MuzzleFlash(humanoid.pos + 22 * direction)

from enum import Enum
from random import random
from typing import Any

from model import GameObject, Timer


class Conditions(Enum):
    RANDOM_RATE = 'random rate'
    COOLDOWN = 'cooldown'
    ENERGY_AVAILABLE = 'energy available'
    DAMAGED = 'damaged'
    ENERGY_NOT_FULL = 'energy not full'
    TARGET_CLOSE = 'target close'
    DEAD = 'dead'
    ALWAYS = 'always'


class Condition(object):
    """Evaluates a boolean function on a Humanoid."""

    def check(self, humanoid: Any) -> bool:
        raise NotImplementedError

    def __or__(self, other: Any) -> object:
        assert isinstance(other, Condition)
        return _Or(self, other)

    def __and__(self, other: Any) -> object:
        assert isinstance(other, Condition)
        return _And(self, other)

    def __invert__(self) -> object:
        return _Not(self)


class _Not(Condition):
    def __init__(self, cond: Condition) -> None:
        self._cond = cond

    def check(self, humanoid: Any) -> bool:
        return not self._cond.check(humanoid)


class _Or(Condition):
    def __init__(self, cond_0: Condition, cond_1: Condition) -> None:
        self._cond_0 = cond_0
        self._cond_1 = cond_1

    def check(self, humanoid: Any) -> bool:
        return self._cond_0.check(humanoid) or self._cond_1.check(humanoid)


class _And(Condition):
    def __init__(self, cond_0: Condition, cond_1: Condition) -> None:
        self._cond_0 = cond_0
        self._cond_1 = cond_1

    def check(self, humanoid: Any) -> bool:
        return self._cond_0.check(humanoid) and self._cond_1.check(humanoid)


class TargetClose(Condition):
    def __init__(self, target: GameObject, close_threshold: float) -> None:
        self._target = target
        self._close_threshold = close_threshold

    def check(self, humanoid: Any) -> bool:
        target_disp = humanoid.pos - self._target.pos
        return target_disp.length() < self._close_threshold


class RandomEventAtRate(Condition):
    """Gives true checks at a given rate.

    It is assumed that check is called at every time step.
    """

    def check(self, humanoid: Any) -> bool:
        return random() < self._timer.dt * self._rate

    def __init__(self, timer: Timer, rate: float) -> None:
        self._timer = timer
        assert rate > 0
        self._rate = rate


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
        return humanoid.status.damaged


class EnergyNotFull(Condition):
    def check(self, humanoid: Any) -> bool:
        source = humanoid.energy_source
        return source.energy_available < source.max_energy


class IsDead(Condition):
    def check(self, humanoid: Any) -> bool:
        return humanoid.status.is_dead


class AlwaysTrue(Condition):
    def check(self, humanoid: Any) -> bool:
        return True
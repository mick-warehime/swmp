from enum import Enum
from random import uniform, choice, random
from typing import Any, List

from pygame.math import Vector2
from pygame.surface import Surface

import sounds

from model import Timer, GameObject
from projectiles import ProjectileData, ProjectileFactory, MuzzleFlash


class Conditions(Enum):
    RANDOM_RATE = 'random rate'
    COOLDOWN = 'cooldown'
    ENERGY_AVAILABLE = 'energy available'
    DAMAGED = 'damaged'
    ENERGY_NOT_FULL = 'energy not full'
    TARGET_CLOSE = 'target close'


class Effects(Enum):
    EQUIP_AND_USE_MOD = 'equip and use mod'
    RANDOM_SOUND = 'play random sound'
    FACE_AND_PURSUE = 'face and pursue target'
    STOP_MOTION = 'stop motion'


class Condition(object):
    """Evaluates a boolean function on a Humanoid."""

    def check(self, humanoid: Any) -> bool:
        raise NotImplementedError

    def __or__(self, other: Any) -> object:
        assert isinstance(other, Condition)
        return _Or(self, other)

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


class Effect(object):
    """Implements an effect on a Humanoid."""

    def activate(self, humanoid: Any) -> None:
        raise NotImplementedError


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


class StopMotion(Effect):
    def activate(self, humanoid: Any) -> None:
        humanoid.motion.stop()


class EquipAndUseMod(Effect):
    def activate(self, humanoid: Any) -> None:
        humanoid.inventory.equip(self._mod)
        humanoid.ability_caller(self._mod.loc)()

    def __init__(self, mod: Any) -> None:
        self._mod = mod


class UpdateLastUse(Effect):
    def __init__(self, cool_down_condition: CooldownCondition) -> None:
        self._cool_down_condition = cool_down_condition

    def activate(self, humanoid: Any) -> None:
        self._cool_down_condition.update_last_use(humanoid)


class Heal(Effect):
    def __init__(self, heal_amount: int) -> None:
        self._heal_amount = heal_amount

    def activate(self, humanoid: Any) -> None:
        humanoid.status.increment_health(self._heal_amount)


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


class PlaySound(Effect):
    def __init__(self, sound_file: str) -> None:
        self._sound_file = sound_file

    def activate(self, humanoid: Any) -> None:
        sounds.play(self._sound_file)


class DrawOnSurface(Effect):
    def activate(self, humanoid: Any) -> None:
        pos = humanoid.pos
        self._drawn_on.blit(self._to_draw, pos - Vector2(32, 32))

    def __init__(self, drawn_on: Surface, to_draw: Surface) -> None:
        self._drawn_on = drawn_on
        self._to_draw = to_draw


class PlayRandomSound(Effect):
    def __init__(self, sound_files: List[str]) -> None:
        assert sound_files, 'At least one sound file must be specified.'
        self._sound_files = sound_files

    def activate(self, humanoid: Any) -> None:
        sound_file = choice(self._sound_files)
        sounds.play(sound_file)


class Kickback(Effect):
    def __init__(self, kickback: int) -> None:
        self._kickback = kickback

    def activate(self, humanoid: Any) -> None:
        humanoid.motion.vel = Vector2(-self._kickback, 0).rotate(
            -humanoid.motion.rot)


class MakeProjectile(Effect):
    def __init__(self, projectile_data: ProjectileData, spread: int,
                 projectile_count: int) -> None:
        self._factory = ProjectileFactory(projectile_data)
        self._spread = spread
        self._count = projectile_count

    def activate(self, humanoid: Any) -> None:
        pos = humanoid.pos
        rot = humanoid.motion.rot

        direction = Vector2(1, 0).rotate(-rot)
        barrel_offset = Vector2(30, 10)
        origin = pos + barrel_offset.rotate(-rot)

        for _ in range(self._count):
            spread = uniform(-self._spread, self._spread)
            self._factory.build(origin, direction.rotate(spread))


class MuzzleFlashEffect(Effect):
    def activate(self, humanoid: Any) -> None:
        direction = humanoid.motion.direction
        direction = direction.rotate(20)
        MuzzleFlash(humanoid.pos + 22 * direction)


class DropItem(Effect):
    def __init__(self, item_label: str) -> None:
        self.item_label = item_label

    def activate(self, humanoid: Any) -> None:
        # TODO(dvirk): I need to import locally to avoid circular import
        # errors. Is this bad?
        from data.constructors import ItemManager
        ItemManager.item(humanoid.pos, self.item_label)


class FaceAndPursueTarget(Effect):
    def __init__(self, target: GameObject) -> None:
        self._target = target

    def activate(self, humanoid: Any) -> None:
        target_disp = self._target.pos - humanoid.pos
        humanoid.motion.rot = target_disp.angle_to(Vector2(1, 0))
        # TODO(dvirk): update_acc is only a method for Enemy. This is a bit
        # kludgy.
        humanoid.update_acc()

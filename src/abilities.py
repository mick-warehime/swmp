"""Module for defining Humanoid abilities."""
from collections import namedtuple
from typing import Any, List

from data.input_output import load_projectile_data_kwargs
from effects import Effect, UpdateLastUse, Heal, Recharge, ExpendEnergy, \
    PlaySound, Kickback, MakeProjectile, MuzzleFlashEffect
from conditions import Condition, CooldownCondition, EnergyAvailable, \
    IsDamaged, EnergyNotFull
from model import TimeAccess
from projectiles import ProjectileData


class Ability(TimeAccess):
    def __init__(self) -> None:

        self._use_effects: List[Effect] = []
        self._use_conditions: List[Condition] = []

        self.uses_left = 0

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
            projectile_data = ProjectileData(**load_projectile_data_kwargs(
                projectile_label))
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

        cool_down = CooldownCondition(data.cool_down_time)
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


class DecrementUses(Effect):
    def __init__(self, ability: Ability) -> None:
        self._used_ability = ability

    def activate(self, humanoid: Any) -> None:
        self._used_ability.uses_left -= 1

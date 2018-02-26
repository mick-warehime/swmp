from typing import Callable, List, Union, NamedTuple
from typing import Dict

import pygame as pg
from pygame.math import Vector2
from pygame.sprite import Group

import items
import model as mdl
import mods


class Backpack(object):
    """Stores the inactive mods available to a Humanoid."""

    def __init__(self) -> None:

        backpack_size = 8
        self.size = 8
        self._slots: List[Union[mods.Mod, None]] = [None] * backpack_size

        self._slots_filled = 0

    @property
    def is_full(self) -> bool:
        return self._slots_filled == self.size

    def add_mod(self, mod: mods.Mod) -> None:
        matching_mods = [md for md in self._slots if md == mod]
        if matching_mods and mod.stackable:
            assert len(matching_mods) == 1
            matching_mods[0].ability.uses_left += mod.ability.uses_left
            return

        self._slots[self._first_empty_slot()] = mod
        self._slots_filled += 1

    def _first_empty_slot(self) -> int:
        assert not self.is_full
        for slot, mod in enumerate(self._slots):
            if mod is None:
                empty_slot = slot
                break
        return empty_slot

    def remove_mod(self, mod: mods.Mod) -> None:
        assert mod in self._slots
        empty_slot = self._slots.index(mod)
        self._slots[empty_slot] = None
        self._slots_filled -= 1

    def slot_occupied(self, slot: int) -> bool:
        return self._slots[slot] is not None

    def __getitem__(self, index: int) -> Union[mods.Mod, None]:
        return self._slots[index]

    def __len__(self) -> int:
        return self.size


class Inventory(object):
    """Stores and updates the mods available to a Humanoid."""

    def __init__(self) -> None:
        self.backpack = Backpack()
        self.active_mods: Dict[mods.ModLocation, mods.Mod] = {}

    def attempt_pickup(self, item: items.ItemObject) -> None:
        if item.mod.loc not in self.active_mods:
            self.equip(item.mod)
            item.kill()
            return
        mod_at_loc = self.active_mods[item.mod.loc]

        if mod_at_loc == item.mod and item.mod.stackable:
            mod_at_loc.ability.uses_left += item.mod.ability.uses_left
            item.kill()
            return

        if not self.backpack.is_full:
            self.backpack.add_mod(item.mod)
            item.kill()
            return

    def unequip(self, loc: mods.ModLocation) -> None:
        assert not self.backpack.is_full
        old_mod = self.active_mods.pop(loc, None)
        if old_mod is not None:
            self.backpack.add_mod(old_mod)

    def equip(self, item_mod: mods.Mod) -> None:
        if item_mod in self.backpack:  # type: ignore
            self.backpack.remove_mod(item_mod)
        self.unequip(item_mod.loc)
        self.active_mods[item_mod.loc] = item_mod


class Status(object):
    """Represents the current state of a Humanoid."""

    def __init__(self, max_health: int) -> None:
        self._max_health = max_health
        self._health = max_health
        self.state = None

    def increment_health(self, amount: int) -> None:
        new_health = self._health + amount
        new_health = min(new_health, self.max_health)
        new_health = max(new_health, 0)
        self._health = new_health

    @property
    def health(self) -> int:
        return self._health

    @property
    def max_health(self) -> int:
        return self._max_health

    @property
    def damaged(self) -> bool:
        return self.health < self._max_health

    @property
    def is_dead(self) -> bool:
        return self.health <= 0


class HumanoidData(NamedTuple):
    status: Status
    inventory: Inventory


class Humanoid(mdl.DynamicObject):
    """DynamicObject with health, inventory, and motion. We will add more to
    this later."""

    def __init__(self, hit_rect: pg.Rect, pos: Vector2,
                 max_health: int) -> None:
        self._check_class_initialized()
        hit_rect = hit_rect.copy()
        hit_rect.center = pos
        self.motion: Motion = Motion(self, self._timer, self._groups.walls,
                                     hit_rect)

        self.status = Status(max_health)
        super().__init__(pos)
        self._base_rect = self.image.get_rect().copy()

        self.inventory = Inventory()

    @property
    def rect(self) -> pg.Rect:
        self._base_rect.center = Vector2(self.pos)
        return self._base_rect

    @property
    def image(self) -> pg.Surface:
        raise NotImplementedError

    def _use_ability_at(self, loc: mods.ModLocation) -> None:
        active_mods = self.inventory.active_mods
        if loc not in active_mods:
            return
        item_mod = active_mods[loc]
        assert loc == item_mod.loc
        assert not item_mod.expended

        if item_mod.ability.can_use(self):
            item_mod.ability.use(self)

        if item_mod.expended:
            active_mods.pop(item_mod.loc)

    def ability_caller(self, loc: mods.ModLocation) -> Callable:
        def called_ability() -> None:
            return self._use_ability_at(loc)

        return called_ability

    def update(self) -> None:
        raise NotImplementedError

    @property
    def data(self) -> HumanoidData:
        return HumanoidData(self.status, self.inventory)

    @data.setter
    def data(self, other: HumanoidData) -> None:
        self.status = other.status
        self.inventory = other.inventory


class Motion(object):
    """Handles movement of Humanoids."""

    def __init__(self, humanoid: Humanoid, timer: mdl.Timer,
                 walls: Group, hit_rect: pg.Rect) -> None:
        self._humanoid = humanoid
        self._timer = timer
        self._walls = walls

        self.vel = Vector2(0, 0)
        self.acc = Vector2(0, 0)
        self.rot = 0
        self.hit_rect = hit_rect

    @property
    def direction(self) -> Vector2:
        return Vector2(1, 0).rotate(-self.rot)

    @property
    def rect(self) -> pg.Rect:
        return self._humanoid.rect

    @property
    def pos(self) -> Vector2:
        return self._humanoid.pos

    @pos.setter
    def pos(self, value: Vector2) -> None:
        self._humanoid.pos = value

    def update(self) -> None:
        self._update_trajectory()
        self._collide_with_walls()

    def _update_trajectory(self) -> None:
        dt = self._timer.dt
        self.vel += self.acc * dt
        self.pos += self.vel * dt

    def _collide_with_walls(self) -> None:
        self.hit_rect.centerx = self.pos.x
        self._collide_walls_in_direction('x')
        self.hit_rect.centery = self.pos.y
        self._collide_walls_in_direction('y')
        # For some reason, mypy cannot infer the type of hit_rect in the line
        #  below.
        self.rect.center = self.hit_rect.center  # type: ignore

    def stop_x(self) -> None:
        self.vel.x = 0
        self.acc.x = 0

    def stop_y(self) -> None:
        self.vel.y = 0
        self.acc.y = 0

    def stop(self) -> None:
        self.stop_x()
        self.stop_y()

    def _collide_walls_in_direction(self, x_or_y: str) -> None:
        assert x_or_y == 'x' or x_or_y == 'y'
        group = self._walls
        if x_or_y == 'x':
            hits = pg.sprite.spritecollide(self._humanoid, group, False,
                                           collide_hit_rect_with_rect)
            if hits:
                if hits[0].rect.centerx > self.hit_rect.centerx:
                    self.pos.x = hits[
                                     0].rect.left - self.hit_rect.width / 2
                if hits[0].rect.centerx <= self.hit_rect.centerx:
                    self.pos.x = hits[
                                     0].rect.right + self.hit_rect.width / 2
                self.stop_x()
                self.hit_rect.centerx = self.pos.x
        if x_or_y == 'y':
            hits = pg.sprite.spritecollide(self._humanoid, group, False,
                                           collide_hit_rect_with_rect)
            if hits:
                if hits[0].rect.centery > self.hit_rect.centery:
                    self.pos.y = hits[
                                     0].rect.top - self.hit_rect.height / 2
                if hits[0].rect.centery <= self.hit_rect.centery:
                    self.pos.y = hits[
                                     0].rect.bottom + self.hit_rect.height / 2
                self.stop_y()
                self.hit_rect.centery = self.pos.y


def collide_hit_rect_with_rect(humanoid: Humanoid,
                               sprite: pg.sprite.Sprite) -> bool:
    """Collide the hit_rect of a Humanoid with the rect of a Sprite. """
    return humanoid.motion.hit_rect.colliderect(sprite.rect)


class EnergySource(object):
    def __init__(self, max_energy: float, recharge_rate: float) -> None:
        self._max_energy = max_energy
        self._recharge_rate = recharge_rate
        self._current_energy = max_energy

    @property
    def fraction_remaining(self) -> float:
        return self._current_energy / self._max_energy

    @property
    def energy_available(self) -> float:
        return self._current_energy

    @property
    def max_energy(self) -> float:
        return self._max_energy

    def increment_energy(self, amount: float) -> None:
        self._current_energy += amount
        self._current_energy = max(self._current_energy, 0)
        self._current_energy = min(self._current_energy, self.max_energy)

    def expend_energy(self, amount: float) -> None:
        assert amount <= self.energy_available
        self._current_energy -= amount

    def passive_recharge(self, dt: float) -> None:
        self.increment_energy(dt * self._recharge_rate)

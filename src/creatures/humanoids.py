from typing import Callable, List, Union
from typing import Dict

import pygame as pg
from pygame.math import Vector2
from pygame.sprite import Group

import model as mdl
import mods
from abilities import EnergyAbility


class Humanoid(mdl.DynamicObject):
    """DynamicObject with health and motion. We will add more to this later."""

    def __init__(self, hit_rect: pg.Rect, pos: Vector2,
                 max_health: int) -> None:
        self._check_class_initialized()
        self._health = max_health
        self._max_health = max_health
        super().__init__(pos)
        self._base_rect = self.image.get_rect().copy()
        # Used in wall collisions
        self.hit_rect: pg.Rect = hit_rect.copy()
        # For some reason, mypy cannot infer the type of hit_rect in the line
        #  below.
        self.hit_rect.center = self.pos  # type: ignore

        self._vel = Vector2(0, 0)
        self._acc = Vector2(0, 0)
        self.rot = 0

        self.backpack = Backpack()
        self.active_mods: Dict[mods.ModLocation, mods.Mod] = {}

    @property
    def _walls(self) -> Group:
        return self._groups.walls

    @property
    def health(self) -> int:
        return self._health

    @property
    def rect(self) -> pg.Rect:
        self._base_rect.center = Vector2(self.pos)
        return self._base_rect

    @property
    def damaged(self) -> bool:
        return self.health < self._max_health

    @property
    def image(self) -> pg.Surface:
        raise NotImplementedError

    def increment_health(self, amount: int) -> None:
        new_health = self._health + amount
        new_health = min(new_health, self._max_health)
        new_health = max(new_health, 0)
        self._health = new_health

    def _update_trajectory(self) -> None:
        dt = self._timer.dt
        self._vel += self._acc * dt
        self.pos += self._vel * dt
        self.pos += 0.5 * self._acc * dt ** 2

    def _collide_with_walls(self) -> None:
        self.hit_rect.centerx = self.pos.x
        _collide_hit_rect_in_direction(self, self._walls, 'x')
        self.hit_rect.centery = self.pos.y
        _collide_hit_rect_in_direction(self, self._walls, 'y')
        # For some reason, mypy cannot infer the type of hit_rect in the line
        #  below.
        self.rect.center = self.hit_rect.center  # type: ignore

    def stop_x(self) -> None:
        self._vel.x = 0

    def stop_y(self) -> None:
        self._vel.y = 0

    def _use_ability_at(self, loc: mods.ModLocation) -> None:
        active_mods = self.active_mods
        if loc not in active_mods:
            return
        item_mod = active_mods[loc]
        assert loc == item_mod.loc
        assert not item_mod.expended

        if item_mod.ability.can_use:
            item_mod.ability.use(self)

        if item_mod.expended:
            active_mods.pop(item_mod.loc)

    def ability_caller(self, loc: mods.ModLocation) -> Callable:
        def called_ability() -> None:
            return self._use_ability_at(loc)

        return called_ability

    def attempt_pickup(self, item: mods.ItemObject) -> None:
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

        # TODO(dvirk): This is rather kludgy and should be implemented more
        # cleanly, probably in an Inventory class.
        if isinstance(item_mod.ability, EnergyAbility):
            assert hasattr(self, 'energy_source'), 'Right now only Players ' \
                                                   'are given an energy  ' \
                                                   'source.'
            item_mod.ability.assign_energy_source(self.energy_source)


class Backpack(object):
    """Stores the mods available to a Humanoid."""

    def __init__(self) -> None:

        backpack_size = 8
        self.size = 8
        self._slots: List[Union[mods.Mod, None]] = [None] * backpack_size

        self._slots_filled = 0

    @property
    def is_full(self) -> bool:
        return self._slots_filled == self.size

    def add_mod(self, mod: mods.Mod) -> None:
        matching_mods = [md for md in self._slots if isinstance(md, type(mod))]
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


def _collide_hit_rect_in_direction(hmn: Humanoid, group: mdl.Group,
                                   x_or_y: str) -> None:
    assert x_or_y == 'x' or x_or_y == 'y'
    if x_or_y == 'x':
        hits = pg.sprite.spritecollide(hmn, group, False,
                                       collide_hit_rect_with_rect)
        if hits:
            if hits[0].rect.centerx > hmn.hit_rect.centerx:
                hmn.pos.x = hits[0].rect.left - hmn.hit_rect.width / 2
            if hits[0].rect.centerx <= hmn.hit_rect.centerx:
                hmn.pos.x = hits[0].rect.right + hmn.hit_rect.width / 2
            hmn.stop_x()
            hmn.hit_rect.centerx = hmn.pos.x
    if x_or_y == 'y':
        hits = pg.sprite.spritecollide(hmn, group, False,
                                       collide_hit_rect_with_rect)
        if hits:
            if hits[0].rect.centery > hmn.hit_rect.centery:
                hmn.pos.y = hits[0].rect.top - hmn.hit_rect.height / 2
            if hits[0].rect.centery <= hmn.hit_rect.centery:
                hmn.pos.y = hits[0].rect.bottom + hmn.hit_rect.height / 2
            hmn.stop_y()
            hmn.hit_rect.centery = hmn.pos.y


def collide_hit_rect_with_rect(humanoid: Humanoid,
                               sprite: pg.sprite.Sprite) -> bool:
    """Collide the hit_rect of a Humanoid with the rect of a Sprite. """
    return humanoid.hit_rect.colliderect(sprite.rect)

from random import random
from typing import NamedTuple, List, Dict

import pygame as pg
from pygame.math import Vector2, Vector3
from pygame.sprite import Group

import images
import settings
import sounds
from creatures.humanoids import Humanoid
from creatures.players import Player
from data.constructors import ItemManager
from data.input_output import load_mod_data_kwargs
from mods import Mod, ModData
from tilemap import ObjectType

MOB_SPEED = 100
MOB_HEALTH = 100
MOB_DAMAGE = 10
MOB_KNOCKBACK = 20
AVOID_RADIUS = 50
DETECT_RADIUS = 400

ModSpec = Dict[str, Dict[str, float]]


class BaseEnemyData(NamedTuple):
    max_speed: int
    max_health: int
    hit_rect: pg.Rect
    image_file: str
    damage: int
    knockback: int
    conflict_group: Group
    mods: List[Mod]
    mod_use_rates: List[float]
    drops_on_kill: str


class EnemyData(BaseEnemyData):
    def __new__(cls, max_speed: float, max_health: int, hit_rect_width: int,
                hit_rect_height: int, image_file: str, damage: int,
                knockback: int = 0, conflict_group: Group = None,
                mod_specs: ModSpec = None, drops_on_kill: str = None) -> \
            BaseEnemyData:  # type:ignore
        hit_rect = pg.Rect(0, 0, hit_rect_width, hit_rect_height)

        mods = []
        mod_rates = []
        if mod_specs is not None:
            for mod_name, spec in mod_specs.items():
                mod = Mod(ModData(**load_mod_data_kwargs(mod_name)))
                rate = spec['rate']
                mods.append(mod)
                mod_rates.append(rate)

        return super().__new__(cls,  # type:ignore
                               max_speed, max_health, hit_rect, image_file,
                               damage, knockback, conflict_group, mods,
                               mod_rates, drops_on_kill)

    def add_quest_group(self, group: Group) -> BaseEnemyData:
        """Generate a new EnemyData with a given conflict group."""
        kwargs = self._asdict()
        kwargs['conflict_group'] = group
        return super().__new__(EnemyData, **kwargs)


mob_data = EnemyData(MOB_SPEED, MOB_HEALTH, 30, 30,  # type: ignore
                     images.MOB_IMG, MOB_DAMAGE, MOB_KNOCKBACK)


class Enemy(Humanoid):
    class_initialized = False
    _map_img: pg.Surface = None

    def __init__(self, pos: Vector2, player: Player, data: EnemyData) -> None:
        self._check_class_initialized()
        self._data = data
        super().__init__(data.hit_rect, pos, data.max_health)

        self.damage = data.damage
        self.knockback = data.knockback

        my_groups = [self._groups.all_sprites, self._groups.mobs]
        if data.conflict_group is not None:
            my_groups.append(data.conflict_group)

        pg.sprite.Sprite.__init__(self, my_groups)

        self.target = player

    def kill(self) -> None:
        if self._data.drops_on_kill is not None:
            ItemManager.item(self.pos, self._data.drops_on_kill)
        sounds.mob_hit_sound()
        splat = images.get_image(images.SPLAT)
        self._map_img.blit(splat, self.pos - Vector2(32, 32))
        super().kill()

    @classmethod
    def init_class(cls, map_img: pg.Surface) -> None:
        if not cls.class_initialized:
            cls._map_img = map_img
            cls.class_initialized = True

    @property
    def image(self) -> pg.Surface:
        base_image = images.get_image(self._data.image_file)
        image = pg.transform.rotate(base_image, self.motion.rot)

        if self.damaged:
            self._draw_health_bar(image, base_image.get_width())
        return image

    def _draw_health_bar(self, image: pg.Surface, full_width: int) -> None:
        col = self._health_bar_color()
        width = int(full_width * self.health / MOB_HEALTH)
        health_bar = pg.Rect(0, 0, width, 7)
        pg.draw.rect(image, col, health_bar)

    def update(self) -> None:
        target_disp = self.target.pos - self.pos
        if self._target_close(target_disp):
            dt = self._timer.dt

            if random() < 0.1 * dt:
                sounds.mob_moan_sound()

            self.motion.rot = target_disp.angle_to(Vector2(1, 0))
            self._update_acc()

            for mod, rate in zip(self._data.mods, self._data.mod_use_rates):
                if random() < rate * dt:
                    self.inventory.equip(mod)
                    self.ability_caller(mod.loc)()
        else:
            self.motion.stop()

        self.motion.update()

        if self.health <= 0:
            self.kill()

    def _check_class_initialized(self) -> None:
        super()._check_class_initialized()
        if not self.class_initialized:
            raise RuntimeError(
                'Enemy class must be initialized before an object'
                ' can be instantiated.')

    def _avoid_mobs(self) -> None:
        for mob in self._groups.mobs:
            if mob is self:
                continue
            dist = self.pos - mob.pos
            if 0 < dist.length() < AVOID_RADIUS:
                self.motion.acc += dist.normalize()

    def _update_acc(self) -> None:
        self.motion.acc = Vector2(1, 0).rotate(-self.motion.rot)
        self._avoid_mobs()
        self.motion.acc.scale_to_length(self._data.max_speed)
        self.motion.acc += self.motion.vel * -1

    @staticmethod
    def _target_close(target_dist: Vector2) -> bool:
        return target_dist.length() < DETECT_RADIUS

    def _health_bar_color(self) -> tuple:
        health_fraction = float(self.health) / self.max_health
        if health_fraction > 0.5:
            frac = 2 * (1 - health_fraction)
            vec = Vector3(settings.GREEN) * frac
            vec += Vector3(settings.YELLOW) * (1 - frac)
            col = tuple(vec)
        else:
            frac = 2 * health_fraction
            vec = Vector3(settings.YELLOW) * frac
            vec += Vector3(settings.RED) * (1 - frac)
            col = tuple(vec)
        return col

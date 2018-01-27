from random import random
from typing import NamedTuple, Any

import pygame as pg
from pygame.math import Vector2, Vector3
from pygame.sprite import Group

import images
import settings
import sounds
from creatures.humanoids import Humanoid
from creatures.players import Player
from data.input_output import load_mod_data_kwargs
from mods import Mod, ModData
from tilemap import ObjectType
from data.constructors import ItemManager

MOB_SPEED = 100
MOB_HEALTH = 100
MOB_DAMAGE = 10
MOB_KNOCKBACK = 20
AVOID_RADIUS = 50
DETECT_RADIUS = 400


class BaseEnemyData(NamedTuple):
    max_speed: int
    max_health: int
    hit_rect: pg.Rect
    damage: int
    knockback: int
    conflict_group: Group


class EnemyData(BaseEnemyData):
    def __new__(cls, max_speed: float, max_health: int, hit_rect_width: int,
                hit_rect_height: int, damage: int, knockback: int = 0,
                conflict_group: Group = None) -> BaseEnemyData:
        hit_rect = pg.Rect(0, 0, hit_rect_width, hit_rect_height)
        return super().__new__(cls, max_speed, max_health, hit_rect, damage,
                               knockback, conflict_group)

    def __init__(self, *args: Any) -> None:
        pass

    def add_quest_group(self, group: Group) -> BaseEnemyData:
        kwargs = self._asdict()
        kwargs['conflict_group'] = group
        return super().__new__(EnemyData, **kwargs)


mob_data = EnemyData(MOB_SPEED, MOB_HEALTH, 30, 30, MOB_DAMAGE, MOB_KNOCKBACK,
                     None)

quest_mob_data = EnemyData(MOB_SPEED * 4, MOB_HEALTH * 2, 30, 30,
                           MOB_DAMAGE * 2, MOB_KNOCKBACK * 2, None)


class Enemy(Humanoid):
    class_initialized = False
    _map_img: pg.Surface = None

    def __init__(self, pos: Vector2, player: Player, data: EnemyData) -> None:
        self._check_class_initialized()
        self._data = data
        self.is_quest = data.conflict_group is not None
        super().__init__(data.hit_rect, pos, data.max_health)

        self.damage = data.damage
        self.knockback = data.knockback

        if self.is_quest:
            my_groups = [self._groups.all_sprites, self._groups.mobs,
                         data.conflict_group]
        else:
            my_groups = [self._groups.all_sprites, self._groups.mobs]

        pg.sprite.Sprite.__init__(self, my_groups)

        self.max_speed = data.max_speed
        self.target = player

        if self.is_quest:
            self._vomit_mod = Mod(ModData(**load_mod_data_kwargs('vomit')))
            self.inventory.active_mods[self._vomit_mod.loc] = self._vomit_mod

    def kill(self) -> None:
        if self.is_quest:
            ItemManager.item(self.pos, ObjectType.PISTOL)
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
        if self.is_quest:
            base_image = images.get_image(images.QMOB_IMG)
        else:
            base_image = images.get_image(images.MOB_IMG)
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

            if random() * dt < 0.00004:
                sounds.mob_moan_sound()

            self.motion.rot = target_disp.angle_to(Vector2(1, 0))
            self._update_acc()

            if self.is_quest and random() * dt < 0.0002:
                self.ability_caller(self._vomit_mod.loc)()
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
        self.motion.acc.scale_to_length(self.max_speed)
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

from random import choice, random

import pygame as pg
from pygame.math import Vector2
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

MOB_SPEEDS = [150, 100, 75, 125]
MOB_HIT_RECT = pg.Rect(0, 0, 30, 30)
MOB_HEALTH = 100
MOB_DAMAGE = 10
MOB_KNOCKBACK = 20
AVOID_RADIUS = 50
DETECT_RADIUS = 400


class Mob(Humanoid):
    class_initialized = False
    _splat = None
    _map_img = None
    damage = MOB_DAMAGE
    knockback = MOB_KNOCKBACK

    def __init__(self, pos: Vector2, player: Player,
                 conflict_group: Group) -> None:
        self._check_class_initialized()
        self.is_quest = conflict_group is not None
        super().__init__(MOB_HIT_RECT, pos, MOB_HEALTH)

        if self.is_quest:
            my_groups = [self._groups.all_sprites, self._groups.mobs,
                         conflict_group]
        else:
            my_groups = [self._groups.all_sprites, self._groups.mobs]

        pg.sprite.Sprite.__init__(self, my_groups)

        self.speed = choice(MOB_SPEEDS)
        self.target = player

        if self.is_quest:
            self.speed *= 2
            self._vomit_mod = Mod(ModData(**load_mod_data_kwargs('vomit')))
            self.inventory.active_mods[self._vomit_mod.loc] = self._vomit_mod

    def kill(self) -> None:
        if self.is_quest:
            ItemManager.item(self.pos, ObjectType.PISTOL)
        sounds.mob_hit_sound()
        self._map_img.blit(self._splat, self.pos - Vector2(32, 32))
        super().kill()

    @classmethod
    def init_class(cls, map_img: pg.Surface) -> None:
        if not cls.class_initialized:
            splat_img = images.get_image(images.SPLAT)
            cls._splat = pg.transform.scale(splat_img, (64, 64))
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
            col = self._health_bar_color()
            width = int(image.get_width() * self.health / MOB_HEALTH)
            health_bar = pg.Rect(0, 0, width, 7)
            pg.draw.rect(image, col, health_bar)
        return image

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
            raise RuntimeError('Mob class must be initialized before an object'
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
        self.motion.acc.scale_to_length(self.speed)
        self.motion.acc += self.motion.vel * -1

    @staticmethod
    def _target_close(target_dist: Vector2) -> bool:
        return target_dist.length() < DETECT_RADIUS

    def _health_bar_color(self) -> tuple:
        if self.health > 60:
            col = settings.GREEN
        elif self.health > 30:
            col = settings.YELLOW
        else:
            col = settings.RED
        return col

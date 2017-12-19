from itertools import chain
from random import choice, random
import pygame as pg
from pygame.math import Vector2
from weapon import Weapon
from typing import List, Dict, Tuple
import math
from pygame.sprite import Group
import images
import mod
import model as mdl
import settings
import sounds
from model import collide_hit_rect_with_rect
from weapon import Weapon


class Humanoid(mdl.DynamicObject):
    """DynamicObject with health and motion. We will add more to this later."""

    def __init__(self, hit_rect: pg.Rect, pos: Vector2,
                 max_health: int) -> None:
        self._check_class_initialized()
        super(Humanoid, self).__init__(hit_rect, pos)
        self._vel = Vector2(0, 0)
        self._acc = Vector2(0, 0)
        self.rot = 0
        self._max_health = max_health
        self._health = max_health
        self.active_mods: Dict[mod.ModLocation, mod.Mod] = {}

        self.backpack: List[mdl.Item] = []
        self.backpack_size = 8

    @property
    def _walls(self) -> Group:
        return self._groups.walls

    @property
    def health(self) -> int:
        return self._health

    @property
    def damaged(self) -> bool:
        return self.health < self._max_health

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
        self.rect.center = self.hit_rect.center

    def _match_image_to_rot(self) -> None:
        self.image = pg.transform.rotate(self.base_image, self.rot)
        self.rect = self.image.get_rect()

    def stop_x(self) -> None:
        self._vel.x = 0

    def stop_y(self) -> None:
        self._vel.y = 0

    def add_item_to_backpack(self, item: mdl.Item) -> None:

        if isinstance(item, mod.Mod):
            if item.loc not in self.active_mods:
                item.use(self)
                return

        self.backpack.append(item)

    def backpack_full(self) -> bool:
        return len(self.backpack) >= self.backpack_size

    def _check_class_initialized(self) -> None:
        super(Humanoid, self)._check_class_initialized()


class Player(Humanoid):
    class_initialized = False

    def __init__(self, pos: Vector2) -> None:

        self._check_class_initialized()

        super(Player, self).__init__(settings.PLAYER_HIT_RECT, pos,
                                     settings.PLAYER_HEALTH)
        pg.sprite.Sprite.__init__(self, self._groups.all_sprites)

        self._weapon = None
        self._damage_alpha = chain(settings.DAMAGE_ALPHA * 4)
        self._rot_speed = 0
        self._mouse_pos = (0, 0)

    def move_towards_mouse(self) -> None:
        self.turn()

        CLOSEST_MOUSE_APPROACH = 10
        if self.distance_to_mouse() < CLOSEST_MOUSE_APPROACH:
            return

        self.move_up()

    def _check_class_initialized(self) -> None:
        super(Player, self)._check_class_initialized()
        if not self.class_initialized:
            raise RuntimeError(
                'Player class must be initialized before an object can be'
                ' instantiated.')

    def move_up(self) -> None:
        self._vel += Vector2(settings.PLAYER_SPEED, 0).rotate(-self.rot)

    def move_down(self) -> None:
        self._vel += Vector2(-settings.PLAYER_SPEED / 2, 0).rotate(-self.rot)

    def move_right(self) -> None:
        self._vel += Vector2(0, settings.PLAYER_SPEED / 2).rotate(-self.rot)

    def move_left(self) -> None:
        self._vel += Vector2(0, -settings.PLAYER_SPEED / 2).rotate(-self.rot)

    def turn(self) -> None:
        self.rotate_towards_cursor()

    def set_weapon(self, label: str) -> None:
        self._weapon = Weapon(label, self._timer, self._groups)

    def shoot(self) -> None:
        if not self._weapon:
            return

        if self._weapon.can_shoot:
            self._weapon.shoot(self.pos, self.rot)
            self._vel = Vector2(-self._weapon.kick_back, 0).rotate(-self.rot)

    def update(self) -> None:

        delta_rot = int(self._rot_speed * self._timer.dt)
        self.rot = (self.rot + delta_rot) % 360

        self._match_image_to_rot()
        self._update_trajectory()
        self._collide_with_walls()

        # reset the movement after each update
        self._rot_speed = 0
        self._vel = Vector2(0, 0)

    def set_rotation(self, rotation: float) -> None:
        self.rot = int(rotation % 360)

    def set_mouse_pos(self, pos: Tuple[int, int]) -> None:
        self._mouse_pos = pos

    def distance_to_mouse(self) -> float:
        x = self._mouse_pos[0] - self.pos[0]
        y = self._mouse_pos[1] - self.pos[1]

        return math.sqrt(x ** 2 + y ** 2)

    def rotate_towards_cursor(self) -> None:
        x = self._mouse_pos[0] - self.pos[0]
        y = self._mouse_pos[1] - self.pos[1]

        angle = -(90 - math.atan2(x, y) * 180 / math.pi) % 360

        self.set_rotation(angle)

    @classmethod
    def init_class(cls) -> None:
        if not cls.class_initialized:
            cls._init_base_image(images.PLAYER_IMG)
            cls.class_initialized = True

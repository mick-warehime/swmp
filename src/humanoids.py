from itertools import chain
from random import choice, random
import pygame as pg
from pygame.sprite import Group
from typing import Tuple, Callable, List
import math
import images
import mods
from pygame.math import Vector2
from typing import Dict
import model as mdl
import settings
import sounds

# Player settings
PLAYER_HEALTH = 100
PLAYER_SPEED = 280
PLAYER_ROT_SPEED = 200
PLAYER_HIT_RECT = pg.Rect(0, 0, 35, 35)

# Mob settings
MOB_SPEEDS = [150, 100, 75, 125]
MOB_HIT_RECT = pg.Rect(0, 0, 30, 30)
MOB_HEALTH = 100
MOB_DAMAGE = 10
MOB_KNOCKBACK = 20
AVOID_RADIUS = 50
DETECT_RADIUS = 400
DAMAGE_ALPHA = list(range(0, 255, 55))


class Humanoid(mdl.DynamicObject):
    """DynamicObject with health and motion. We will add more to this later."""

    def __init__(self, hit_rect: pg.Rect, pos: Vector2,
                 max_health: int) -> None:
        self._check_class_initialized()
        super().__init__(pos)

        # Used in wall collisions
        self.hit_rect: pg.Rect = hit_rect.copy()
        # For some reason, mypy cannot infer the type of hit_rect in the line
        #  below.
        self.hit_rect.center = self.rect.center  # type: ignore

        self._vel = Vector2(0, 0)
        self._acc = Vector2(0, 0)
        self.rot = 0
        self._max_health = max_health
        self._health = max_health
        self.active_mods: Dict[mods.ModLocation, mods.Mod] = {}

        self.backpack: List[mods.Mod] = []
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

    def _match_image_to_rot(self) -> None:
        self.image = pg.transform.rotate(self.base_image, self.rot)
        self.rect = self.image.get_rect()

    def stop_x(self) -> None:
        self._vel.x = 0

    def stop_y(self) -> None:
        self._vel.y = 0

    def equip(self, item_mod: mods.Mod) -> None:
        if item_mod in self.backpack:
            self.backpack.remove(item_mod)
        self._move_mod_at_loc_to_backpack(item_mod.loc)
        self.active_mods[item_mod.loc] = item_mod

    def ability_caller(self, loc: mods.ModLocation) -> Callable:
        def called_ability() -> None:
            return self._use_ability_at(loc)

        return called_ability

    def _use_ability_at(self, loc: mods.ModLocation) -> None:
        if loc not in self.active_mods:
            return
        item_mod = self.active_mods[loc]
        assert loc == item_mod.loc
        assert not item_mod.expended

        if item_mod.ability.can_use:
            item_mod.ability.use(self)

        if item_mod.expended:
            self.active_mods.pop(item_mod.loc)

    def _move_mod_at_loc_to_backpack(self, loc: mods.ModLocation) -> None:
        assert not self.backpack_full
        old_mod = self.active_mods.pop(loc, None)
        if old_mod is not None:
            self.backpack.append(old_mod)

    def attempt_pickup(self, item: mods.ItemObject) -> None:

        if item.mod.loc not in self.active_mods:
            self.equip(item.mod)
            item.kill()
        elif not self.backpack_full:
            self.backpack.append(item.mod)
            item.kill()

    @property
    def backpack_full(self) -> bool:
        return len(self.backpack) >= self.backpack_size


class Player(Humanoid):
    class_initialized = True

    def __init__(self, pos: Vector2) -> None:

        self._check_class_initialized()

        super().__init__(PLAYER_HIT_RECT, pos, PLAYER_HEALTH)
        pg.sprite.Sprite.__init__(self, self._groups.all_sprites)

        self.max_health = PLAYER_HEALTH
        self._damage_alpha = chain(DAMAGE_ALPHA * 4)
        self._rot_speed = 0
        self._mouse_pos = (0, 0)

    def move_towards_mouse(self) -> None:
        self.turn()

        closest_approach = 10
        if self.distance_to_mouse() < closest_approach:
            return

        self.step_forward()

    @property
    def image(self) -> pg.Surface:
        return images.get_image(images.PLAYER_IMG)

    def _check_class_initialized(self) -> None:
        super()._check_class_initialized()
        if not self.class_initialized:
            raise RuntimeError(
                'Player class must be initialized before an object can be'
                ' instantiated.')

    # translate_direction = slide in that direction
    def translate_up(self) -> None:
        self._vel += Vector2(0, -PLAYER_SPEED)

    def translate_down(self) -> None:
        self._vel += Vector2(0, PLAYER_SPEED)

    def translate_right(self) -> None:
        self._vel += Vector2(PLAYER_SPEED, 0)

    def translate_left(self) -> None:
        self._vel += Vector2(-PLAYER_SPEED, 0)

    # step_direction - rotates player towards the current direction
    # and then takes a step relative to that direction
    def step_forward(self) -> None:
        self._vel += Vector2(PLAYER_SPEED, 0).rotate(-self.rot)

    def step_backward(self) -> None:
        self._vel += Vector2(-PLAYER_SPEED, 0).rotate(-self.rot)

    def step_right(self) -> None:
        self._vel += Vector2(0, PLAYER_SPEED).rotate(-self.rot)

    def step_left(self) -> None:
        self._vel += Vector2(0, -PLAYER_SPEED).rotate(-self.rot)

    def turn(self) -> None:
        self.rotate_towards_cursor()

    def update(self) -> None:
        self.turn()
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


class Mob(Humanoid):
    class_initialized = False
    _splat = None
    _map_img = None

    def __init__(self, pos: Vector2, player: Player, quest: bool) -> None:

        self._check_class_initialized()

        super().__init__(MOB_HIT_RECT, pos, MOB_HEALTH)

        if quest:
            my_groups = [self._groups.all_sprites, self._groups.mobs,
                         self._groups.conflicts]
        else:
            my_groups = [self._groups.all_sprites, self._groups.mobs]

        pg.sprite.Sprite.__init__(self, my_groups)

        self.speed = choice(MOB_SPEEDS)
        self.target = player

        if quest:
            self.base_image = images.get_image(images.QMOB_IMG)
            self.speed *= 2

    @property
    def _mob_group(self) -> Group:
        return self._groups.mobs

    def _check_class_initialized(self) -> None:
        super()._check_class_initialized()
        if not self.class_initialized:
            raise RuntimeError(
                'Mob class must be initialized before an object can be'
                ' instantiated.')

    @classmethod
    def init_class(cls, map_img: pg.Surface) -> None:
        if not cls.class_initialized:
            splat_img = images.get_image(images.SPLAT)
            cls._splat = pg.transform.scale(splat_img, (64, 64))
            cls._map_img = map_img
            cls.class_initialized = True

    @property
    def image(self) -> pg.Surface:
        return images.get_image(images.MOB_IMG)

    def _avoid_mobs(self) -> None:
        for mob in self._mob_group:
            if mob != self:
                dist = self.pos - mob.pos
                if 0 < dist.length() < AVOID_RADIUS:
                    self._acc += dist.normalize()

    def update(self) -> None:
        target_dist = self.target.pos - self.pos
        if self._target_close(target_dist):
            if random() < 0.002:
                sounds.mob_moan_sound()
            self.rot = target_dist.angle_to(Vector2(1, 0))

            self._match_image_to_rot()
            self._update_acc()
            self._update_trajectory()
            self._collide_with_walls()

        if self.health <= 0:
            sounds.mob_hit_sound()
            self.kill()
            self._map_img.blit(self._splat, self.pos - Vector2(32, 32))

    def _update_acc(self) -> None:
        self._acc = Vector2(1, 0).rotate(-self.rot)
        self._avoid_mobs()
        self._acc.scale_to_length(self.speed)
        self._acc += self._vel * -1

    @staticmethod
    def _target_close(target_dist: Vector2) -> bool:
        return target_dist.length_squared() < DETECT_RADIUS ** 2

    def draw_health(self) -> None:
        if self.health > 60:
            col = settings.GREEN
        elif self.health > 30:
            col = settings.YELLOW
        else:
            col = settings.RED
        width = int(self.rect.width * self.health / MOB_HEALTH)
        health_bar = pg.Rect(0, 0, width, 7)
        if self.damaged:
            pg.draw.rect(self.image, col, health_bar)


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

from itertools import chain
from random import choice, random
from pygame.math import Vector2
from weapon import Weapon
from typing import List
import model as mdl
import settings
import images
import sounds
import pygame as pg


class Humanoid(mdl.GameObject):
    """GameObject with health and motion. We will add more to this later."""
    humanoids_initialized = False
    _walls = None
    _timer = None

    def __init__(self, hit_rect: pg.Rect, pos: Vector2,
                 max_health: int) -> None:
        super(Humanoid, self).__init__(hit_rect, pos)
        self._vel = Vector2(0, 0)
        self._acc = Vector2(0, 0)
        self.rot = 0
        self._max_health = max_health
        self._health = max_health
        self.skills: List[str] = [settings.PISTOL_SKILL]
        self.active_skills: List[str] = [settings.PISTOL_SKILL]
        self.backpack: List[mdl.Item] = []
        self.backpack_size = 8

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

    def add_skill(self, skill_name: str) -> None:
        self.skills.append(skill_name)
        self.active_skills.append(skill_name)

    def add_item_to_backpack(self, item: mdl.Item) -> None:
        self.backpack.append(item)

    def backpack_full(self) -> bool:
        return len(self.backpack) >= self.backpack_size

    @classmethod
    def init_class(cls, walls: mdl.Group, timer: mdl.Timer):
        if not cls.humanoids_initialized:
            cls._walls = walls
            cls._timer = timer
            cls.humanoids_initialized = True


class Player(Humanoid):
    class_initialized = False

    def __init__(self, groups: mdl.Groups, pos: Vector2) -> None:

        if not (self.class_initialized and self.humanoids_initialized):
            raise ValueError('Classes %s and %s must be initialized before an '
                             'object can be instantiated.' % (Player, Humanoid))

        super(Player, self).__init__(settings.PLAYER_HIT_RECT, pos,
                                     settings.PLAYER_HEALTH)
        pg.sprite.Sprite.__init__(self, groups.all_sprites)

        self._weapon = Weapon('pistol', self._timer, groups)
        self._damage_alpha = chain(settings.DAMAGE_ALPHA * 4)
        self._rot_speed = 0

    def move_up(self) -> None:
        self._vel += Vector2(settings.PLAYER_SPEED, 0).rotate(-self.rot)

    def move_down(self) -> None:
        self._vel += Vector2(-settings.PLAYER_SPEED / 2, 0).rotate(-self.rot)

    def move_right(self) -> None:
        self._vel += Vector2(0, settings.PLAYER_SPEED / 2).rotate(-self.rot)

    def move_left(self) -> None:
        self._vel += Vector2(0, -settings.PLAYER_SPEED / 2).rotate(-self.rot)

    def turn_clockwise(self) -> None:
        self._rot_speed = -settings.PLAYER_ROT_SPEED * 2

    def turn_counterclockwise(self) -> None:
        self._rot_speed = settings.PLAYER_ROT_SPEED * 2

    def set_weapon(self, weapon: str) -> None:
        self._weapon.set(weapon)

    def shoot(self) -> None:
        if self._weapon.can_shoot:
            self._weapon.shoot(self.pos, self.rot)
            self._vel = Vector2(-self._weapon.kick_back, 0).rotate(-self.rot)

    def update(self) -> None:

        if self.damaged:
            try:
                self.image.fill((255, 255, 255, next(self._damage_alpha)),
                                special_flags=pg.BLEND_RGBA_MULT)
            except StopIteration:
                pass

        delta_rot = int(self._rot_speed * self._timer.dt)
        self.rot = (self.rot + delta_rot) % 360

        self._match_image_to_rot()
        self._update_trajectory()
        self._collide_with_walls()

        # reset the movement after each update
        self._rot_speed = 0
        self._vel = Vector2(0, 0)

    @classmethod
    def init_class(cls) -> None:
        if not cls.class_initialized:
            cls._init_base_image(images.PLAYER_IMG)
            cls.class_initialized = True


class Mob(Humanoid):
    class_initialized = False
    _splat = None
    _map_img = None
    _mob_group = None

    def __init__(self, pos: Vector2, groups: mdl.Groups, player: Player) -> None:

        if not (self.class_initialized and self.humanoids_initialized):
            raise ValueError('Classes %s and %s must be initialized before an '
                             'object can be instantiated.' % (Mob, Humanoid))

        super(Mob, self).__init__(settings.MOB_HIT_RECT, pos,
                                  settings.MOB_HEALTH)
        pg.sprite.Sprite.__init__(self, [groups.all_sprites, groups.mobs])

        self.speed = choice(settings.MOB_SPEEDS)
        self.target = player

    @classmethod
    def init_class(cls, map_img: pg.Surface, groups: mdl.Groups) -> None:
        if not cls.class_initialized:
            cls._init_base_image(images.MOB_IMG)
            splat_img = images.get_image(images.SPLAT)
            cls._splat = pg.transform.scale(splat_img, (64, 64))
            cls._map_img = map_img
            cls._mob_group = groups.mobs
            cls.class_initialized = True

    def _avoid_mobs(self) -> None:
        for mob in self._mob_group:
            if mob != self:
                dist = self.pos - mob.pos
                if 0 < dist.length() < settings.AVOID_RADIUS:
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
        return target_dist.length_squared() < settings.DETECT_RADIUS ** 2

    def draw_health(self) -> None:
        if self.health > 60:
            col = settings.GREEN
        elif self.health > 30:
            col = settings.YELLOW
        else:
            col = settings.RED
        width = int(self.rect.width * self.health / settings.MOB_HEALTH)
        health_bar = pg.Rect(0, 0, width, 7)
        if self.damaged:
            pg.draw.rect(self.image, col, health_bar)


def collide_hit_rect_with_rect(one: pg.sprite.Sprite,
                               two: pg.sprite.Sprite) -> bool:
    """

    :param one: A Sprite object with a hit_rect field.
    :param two: A Sprite object with a rect field.
    :return: Whether the hit_rect and rect collide.
    """
    return one.hit_rect.colliderect(two.rect)


def _collide_hit_rect_in_direction(hmn: Humanoid, group: mdl.Group,
                                   x_or_y: str) -> None:
    """

    :param hmn: A sprite object with a hit_rect
    :param group:
    :param x_or_y:
    :return:
    """
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

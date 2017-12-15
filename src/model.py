import pygame as pg
from random import uniform, choice, randint, random
from typing import Any, Union
from pygame.math import Vector2
from pygame.sprite import Sprite, Group, LayeredUpdates
import pytweening as tween
from itertools import chain
import settings
import sounds
import images
from collections import namedtuple

_GroupsBase = namedtuple('_GroupsBase',
                         ('walls', 'bullets', 'items', 'mobs', 'all_sprites'))


def collide_hit_rect_with_rect(one: pg.sprite.Sprite,
                               two: pg.sprite.Sprite) -> bool:
    """

    :param one: A Sprite object with a hit_rect field.
    :param two: A Sprite object with a rect field.
    :return: Whether the hit_rect and rect collide.
    """
    return one.hit_rect.colliderect(two.rect)


def _collide_hit_rect_in_direction(sprite: Sprite, group: Group,
                                   x_or_y: str) -> None:
    """

    :param sprite: A sprite object with a hit_rect
    :param group:
    :param x_or_y:
    :return:
    """
    assert x_or_y == 'x' or x_or_y == 'y'
    if x_or_y == 'x':
        hits = pg.sprite.spritecollide(sprite, group, False,
                                       collide_hit_rect_with_rect)
        if hits:
            if hits[0].rect.centerx > sprite.hit_rect.centerx:
                sprite.pos.x = hits[0].rect.left - sprite.hit_rect.width / 2
            if hits[0].rect.centerx <= sprite.hit_rect.centerx:
                sprite.pos.x = hits[0].rect.right + sprite.hit_rect.width / 2
            sprite.vel.x = 0
            sprite.hit_rect.centerx = sprite.pos.x
    if x_or_y == 'y':
        hits = pg.sprite.spritecollide(sprite, group, False,
                                       collide_hit_rect_with_rect)
        if hits:
            if hits[0].rect.centery > sprite.hit_rect.centery:
                sprite.pos.y = hits[0].rect.top - sprite.hit_rect.height / 2
            if hits[0].rect.centery <= sprite.hit_rect.centery:
                sprite.pos.y = hits[0].rect.bottom + sprite.hit_rect.height / 2
            sprite.vel.y = 0
            sprite.hit_rect.centery = sprite.pos.y


class Groups(_GroupsBase):
    """Immutable container object for groups in the game."""

    def __new__(cls) -> _GroupsBase:
        args = [Group() for _ in range(4)]
        args += [LayeredUpdates()]
        return super(Groups, cls).__new__(cls, *args)  # type: ignore


class Timer(object):
    """Keeps track of game time."""

    def __init__(self, controller: Any) -> None:
        self._dungeon_controller = controller

    @property
    def dt(self) -> float:
        return self._dungeon_controller.dt

    @property
    def current_time(self) -> int:
        return pg.time.get_ticks()


class GameObject(pg.sprite.Sprite):
    """In-game object with a body for collisions and an image.

    Added functionality derived from Sprite:
    Can be added/removed to Group objects --> add(*groups), remove(*groups).
    kill() removes from all groups.
    update() method that is referenced when a group is updated.
    alive() : True iff sprite belongs to any group.

    """
    base_image: Union[pg.Surface, None] = None

    def __init__(self, image_file: str, hit_rect: pg.Rect,
                 pos: Vector2) -> None:
        self._init_base_image(image_file)

        self.image = self.base_image
        self.pos = pos
        # Used in sprite collisions other than walls.
        self.rect = self.image.get_rect()
        self.rect.center = (pos.x, pos.y)

        # Used in wall collisions
        self.hit_rect = hit_rect.copy()
        self.hit_rect.center = self.rect.center

    @classmethod
    def _init_base_image(cls, image_file: str) -> None:
        if cls.base_image is None:
            cls.base_image = images.get_image(image_file)


class Humanoid(GameObject):
    """GameObject with health and motion. We will add more to this later."""

    def __init__(self, image_file: str, hit_rect: pg.Rect, pos: Vector2,
                 max_health: int, timer: Timer, walls: Group) -> None:
        super(Humanoid, self).__init__(image_file, hit_rect, pos)
        self.vel = Vector2(0, 0)
        self.acc = Vector2(0, 0)
        self.rect.center = self.pos
        self.rot = 0
        self._max_health = max_health
        self._health = max_health
        self._timer = timer
        self._walls = walls

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
        self.vel += self.acc * dt
        self.pos += self.vel * dt
        self.pos += 0.5 * self.acc * dt ** 2

    def _collide_with_walls(self) -> None:
        self.hit_rect.centerx = self.pos.x
        _collide_hit_rect_in_direction(self, self._walls, 'x')
        self.hit_rect.centery = self.pos.y
        _collide_hit_rect_in_direction(self, self._walls, 'y')
        self.rect.center = self.hit_rect.center

    def _match_image_to_rot(self) -> None:
        self.image = pg.transform.rotate(self.base_image, self.rot)
        self.rect = self.image.get_rect()


class Weapon(object):
    """Generates bullets or other sources of damage."""

    def __init__(self, label: str, timer: Timer, groups: Groups) -> None:
        self._label = ''
        self.set(label)
        self._timer = timer
        self._groups = groups
        self._last_shot = timer.current_time

    def set(self, label: str) -> None:
        if label not in settings.WEAPONS:
            raise ValueError('Weapon \'%s\' not defined in settings.py. '
                             'Allowed values: %s.'
                             % (label, settings.WEAPONS.keys()))
        self._label = label

    @property
    def shoot_rate(self) -> int:
        return settings.WEAPONS[self._label]['rate']

    @property
    def kick_back(self) -> int:
        return settings.WEAPONS[self._label]['kickback']

    @property
    def bullet_count(self) -> int:
        return settings.WEAPONS[self._label]['bullet_count']

    @property
    def spread(self) -> int:
        return settings.WEAPONS[self._label]['spread']

    def shoot(self, pos: Vector2, rot: Vector2) -> None:
        self._last_shot = self._timer.current_time
        direction = Vector2(1, 0).rotate(-rot)
        origin = pos + settings.BARREL_OFFSET.rotate(-rot)

        for _ in range(self.bullet_count):
            spread = uniform(-self.spread, self.spread)
            Bullet(self._timer, self._groups, origin,
                   direction.rotate(spread), self._label)
            sounds.fire_weapon_sound(self._label)
        MuzzleFlash(self._groups.all_sprites, origin)

    @property
    def can_shoot(self) -> bool:
        now = self._timer.current_time
        return now - self._last_shot > self.shoot_rate


class Player(Humanoid):
    def __init__(self, groups: Groups, timer: Timer, pos: Vector2) -> None:

        super(Player, self).__init__(images.PLAYER_IMG,
                                     settings.PLAYER_HIT_RECT, pos,
                                     settings.PLAYER_HEALTH, timer,
                                     groups.walls)
        pg.sprite.Sprite.__init__(self, groups.all_sprites)

        self._weapon = Weapon('pistol', self._timer, groups)
        self.damage_alpha = chain(settings.DAMAGE_ALPHA * 4)
        self.rot_speed = 0

    def move_up(self) -> None:
        self.vel += Vector2(settings.PLAYER_SPEED, 0).rotate(-self.rot)

    def move_down(self) -> None:
        self.vel += Vector2(-settings.PLAYER_SPEED / 2, 0).rotate(-self.rot)

    def move_right(self) -> None:
        self.vel += Vector2(0, settings.PLAYER_SPEED / 2).rotate(-self.rot)

    def move_left(self) -> None:
        self.vel += Vector2(0, -settings.PLAYER_SPEED / 2).rotate(-self.rot)

    def turn_clockwise(self) -> None:
        self.rot_speed = -settings.PLAYER_ROT_SPEED * 2

    def turn_counterclockwise(self) -> None:
        self.rot_speed = settings.PLAYER_ROT_SPEED * 2

    def set_weapon(self, weapon: str) -> None:
        self._weapon.set(weapon)

    def shoot(self) -> None:
        if self._weapon.can_shoot:
            self._weapon.shoot(self.pos, self.rot)
            self.vel = Vector2(-self._weapon.kick_back, 0).rotate(-self.rot)

    def update(self) -> None:

        if self.damaged:
            try:
                self.image.fill((255, 255, 255, next(self.damage_alpha)),
                                special_flags=pg.BLEND_RGBA_MULT)
            except StopIteration:
                pass

        delta_rot = int(self.rot_speed * self._timer.dt)
        self.rot = (self.rot + delta_rot) % 360

        self._match_image_to_rot()
        self._update_trajectory()
        self._collide_with_walls()

        # reset the movement after each update
        self.rot_speed = 0
        self.vel = Vector2(0, 0)


class Mob(Humanoid):
    def __init__(self, pos: Vector2, groups: Groups, timer: Timer,
                 map_img: pg.Surface, player: Player) -> None:

        super(Mob, self).__init__(images.MOB_IMG, settings.MOB_HIT_RECT, pos,
                                  settings.MOB_HEALTH, timer,
                                  groups.walls)
        self._mob_group = groups.mobs
        self._map_img = map_img
        pg.sprite.Sprite.__init__(self, [groups.all_sprites, groups.mobs])

        self.speed = choice(settings.MOB_SPEEDS)
        self.target = player

        splat_img = images.get_image(images.SPLAT)
        self.splat = pg.transform.scale(splat_img, (64, 64))

    def _avoid_mobs(self) -> None:
        for mob in self._mob_group:
            if mob != self:
                dist = self.pos - mob.pos
                if 0 < dist.length() < settings.AVOID_RADIUS:
                    self.acc += dist.normalize()

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
            self._map_img.blit(self.splat, self.pos - Vector2(32, 32))

    def _update_acc(self) -> None:
        self.acc = Vector2(1, 0).rotate(-self.rot)
        self._avoid_mobs()
        self.acc.scale_to_length(self.speed)
        self.acc += self.vel * -1

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


class Bullet(pg.sprite.Sprite):
    def __init__(self, timer: Timer, groups: Groups, pos: Vector2,
                 direction: Vector2, weapon: str) -> None:
        groups_list = [groups.all_sprites, groups.bullets]
        pg.sprite.Sprite.__init__(self, groups_list)
        self._timer = timer
        self._walls = groups.walls
        self.weapon = weapon

        blt_img = images.get_image(images.BULLET_IMG)

        if weapon == 'pistol':
            self.image = blt_img
        else:
            self.image = pg.transform.scale(blt_img, (10, 10))
        self.rect = self.image.get_rect()
        self.hit_rect = self.rect
        self.pos = Vector2(pos)
        self.rect.center = pos

        speed = settings.WEAPONS[weapon]['bullet_speed']
        self.vel = direction * speed * uniform(0.9, 1.1)
        self.spawn_time = self._timer.current_time
        self.damage = settings.WEAPONS[weapon]['damage']

    def update(self) -> None:
        self.pos += self.vel * self._timer.dt
        self.rect.center = self.pos
        if pg.sprite.spritecollideany(self, self._walls):
            self.kill()
        if self._lifetime_exceeded():
            self.kill()

    def _lifetime_exceeded(self) -> bool:
        lifetime = self._timer.current_time - self.spawn_time
        max_time = settings.WEAPONS[self.weapon]['bullet_lifetime']
        return lifetime > max_time


class Obstacle(pg.sprite.Sprite):
    def __init__(self, walls: Group, pos: Vector2, w: int, h: int) -> None:
        pg.sprite.Sprite.__init__(self, walls)

        self.rect = pg.Rect(pos.x, pos.y, w, h)

    @property
    def x(self) -> int:
        return self.rect.x

    @property
    def y(self) -> int:
        return self.rect.y

    @property
    def hit_rect(self) -> pg.Rect:
        return self.rect


class MuzzleFlash(pg.sprite.Sprite):
    def __init__(self, all_sprites: Group, pos: Vector2) -> None:
        pg.sprite.Sprite.__init__(self, all_sprites)
        size = randint(20, 50)

        flash_img = images.get_muzzle_flash()
        self.image = pg.transform.scale(flash_img, (size, size))

        self.rect = self.image.get_rect()
        self.pos = pos
        self.rect.center = pos
        self.spawn_time = pg.time.get_ticks()

    def update(self) -> None:
        if pg.time.get_ticks() - self.spawn_time > settings.FLASH_DURATION:
            self.kill()


class Item(pg.sprite.Sprite):
    def __init__(self, groups: Groups, pos: pg.math.Vector2,
                 label: str) -> None:
        pg.sprite.Sprite.__init__(self, [groups.all_sprites, groups.items])

        self.image = images.get_item_image(label)
        self.rect = self.image.get_rect()
        self.label = label
        self.pos = pos
        self.rect.center = pos
        self.tween = tween.easeInOutSine
        self.step = 0
        self.dir = 1

    def update(self) -> None:
        # bobbing motion
        offset = settings.BOB_RANGE * (
            self.tween(self.step / settings.BOB_RANGE) - 0.5)
        self.rect.centery = self.pos.y + offset * self.dir
        self.step += settings.BOB_SPEED
        if self.step > settings.BOB_RANGE:
            self.step = 0
            self.dir *= -1

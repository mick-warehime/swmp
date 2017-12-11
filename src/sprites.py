import pygame as pg
from random import uniform, choice, randint, random

from typing import Any

from os import path
from pygame.math import Vector2
from pygame.sprite import Sprite, Group

from settings import PLAYER_LAYER, PLAYER_HIT_RECT, PLAYER_HEALTH, \
    PLAYER_ROT_SPEED, PLAYER_SPEED, WEAPONS, DAMAGE_ALPHA, \
    MOB_HIT_RECT, MOB_HEALTH, MOB_SPEEDS, AVOID_RADIUS, DETECT_RADIUS, GREEN, \
    YELLOW, RED, BULLET_LAYER, EFFECTS_LAYER, FLASH_DURATION, ITEMS_LAYER, \
    BOB_RANGE, BOB_SPEED, BARREL_OFFSET, PLAYER_IMG, MOB_IMG, MUZZLE_FLASHES, \
    SPLAT, BULLET_IMG, ITEM_IMAGES
from tilemap import collide_hit_rect
import pytweening as tween
from itertools import chain
import sounds


def collide_with_walls(sprite: Sprite, group: Group, x_or_y: str) -> None:
    if x_or_y == 'x':
        hits = pg.sprite.spritecollide(sprite, group, False, collide_hit_rect)
        if hits:
            if hits[0].rect.centerx > sprite.hit_rect.centerx:
                sprite.pos.x = hits[0].rect.left - sprite.hit_rect.width / 2
            if hits[0].rect.centerx < sprite.hit_rect.centerx:
                sprite.pos.x = hits[0].rect.right + sprite.hit_rect.width / 2
            sprite.vel.x = 0
            sprite.hit_rect.centerx = sprite.pos.x
    if x_or_y == 'y':
        hits = pg.sprite.spritecollide(sprite, group, False, collide_hit_rect)
        if hits:
            if hits[0].rect.centery > sprite.hit_rect.centery:
                sprite.pos.y = hits[0].rect.top - sprite.hit_rect.height / 2
            if hits[0].rect.centery < sprite.hit_rect.centery:
                sprite.pos.y = hits[0].rect.bottom + sprite.hit_rect.height / 2
            sprite.vel.y = 0
            sprite.hit_rect.centery = sprite.pos.y


class Humanoid(pg.sprite.Sprite):
    base_image: pg.Surface = None

    def __init__(self, image_file: str, x: int, y: int) -> None:
        self._init_base_image(image_file)

        self.image = self.base_image
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)

    @classmethod
    def _init_base_image(cls, image_file: str) -> None:
        if cls.base_image is None:
            game_folder = path.dirname(__file__)
            img_folder = path.join(game_folder, 'img')
            image_path = path.join(img_folder, image_file)
            cls.base_image = pg.image.load(image_path).convert_alpha()


class Player(Humanoid):
    def __init__(self, game: Any, x: int, y: int) -> None:

        super(Player, self).__init__(PLAYER_IMG, x, y)

        self._layer = PLAYER_LAYER
        self.groups = game.all_sprites
        pg.sprite.Sprite.__init__(self, self.groups)
        self.game = game

        self.hit_rect = PLAYER_HIT_RECT
        self.hit_rect.center = self.rect.center
        self.vel = Vector2(0, 0)
        self.pos = Vector2(x, y)
        self.rot = 0
        self.last_shot = 0
        self.health = PLAYER_HEALTH
        self.weapon = 'pistol'
        self.damaged = False
        self.rot_speed = 0
        self.vel = Vector2(0, 0)

    def move_up(self) -> None:
        self.vel += Vector2(PLAYER_SPEED, 0).rotate(-self.rot)

    def move_down(self) -> None:
        self.vel += Vector2(-PLAYER_SPEED / 2, 0).rotate(-self.rot)

    def move_right(self) -> None:
        self.vel += Vector2(0, PLAYER_SPEED / 2).rotate(-self.rot)

    def move_left(self) -> None:
        self.vel += Vector2(0, -PLAYER_SPEED / 2).rotate(-self.rot)

    def turn_clockwise(self) -> None:
        self.rot_speed = -PLAYER_ROT_SPEED * 2

    def turn_counterclockwise(self) -> None:
        self.rot_speed = PLAYER_ROT_SPEED * 2

    def shoot(self) -> None:
        now = pg.time.get_ticks()
        if now - self.last_shot > WEAPONS[self.weapon]['rate']:
            self.last_shot = now
            dir = Vector2(1, 0).rotate(-self.rot)
            pos = self.pos + BARREL_OFFSET.rotate(-self.rot)
            self.vel = Vector2(-WEAPONS[self.weapon]['kickback'], 0).rotate(
                -self.rot)
            for i in range(WEAPONS[self.weapon]['bullet_count']):
                spread = uniform(-WEAPONS[self.weapon]['spread'],
                                 WEAPONS[self.weapon]['spread'])
                Bullet(self.game, pos, dir.rotate(spread), self.weapon)
                sounds.fire_weapon_sound(self.weapon)
            MuzzleFlash(self.game, pos)

    def hit(self) -> None:
        self.damaged = True
        self.damage_alpha = chain(DAMAGE_ALPHA * 4)

    def update(self) -> None:
        self.rot = (self.rot + self.rot_speed * self.game.dt) % 360
        self.image = pg.transform.rotate(self.base_image, self.rot)
        if self.damaged:
            try:
                self.image.fill((255, 255, 255, next(self.damage_alpha)),
                                special_flags=pg.BLEND_RGBA_MULT)
            except StopIteration:
                self.damaged = False
        self.rect = self.image.get_rect()
        self.rect.center = self.pos
        self.pos += self.vel * self.game.dt
        self.hit_rect.centerx = self.pos.x
        collide_with_walls(self, self.game.walls, 'x')
        self.hit_rect.centery = self.pos.y
        collide_with_walls(self, self.game.walls, 'y')
        self.rect.center = self.hit_rect.center

        # reset the movement after each update
        self.rot_speed = 0
        self.vel = Vector2(0, 0)

    def add_health(self, amount: int) -> None:
        self.health += amount
        if self.health > PLAYER_HEALTH:
            self.health = PLAYER_HEALTH


class Mob(Humanoid):
    def __init__(self, game: Any, x: int, y: int) -> None:

        super(Mob, self).__init__(MOB_IMG, x, y)

        self.groups = game.all_sprites, game.mobs
        pg.sprite.Sprite.__init__(self, self.groups)

        self.game = game

        self.hit_rect = MOB_HIT_RECT.copy()
        self.hit_rect.center = self.rect.center
        self.pos = Vector2(x, y)
        self.vel = Vector2(0, 0)
        self.acc = Vector2(0, 0)
        self.rect.center = self.pos
        self.rot = 0
        self.health = MOB_HEALTH
        self.speed = choice(MOB_SPEEDS)
        self.target = game.player

        game_folder = path.dirname(__file__)
        img_folder = path.join(game_folder, 'img')
        splat_img_path = path.join(img_folder, SPLAT)
        splat = pg.image.load(splat_img_path).convert_alpha()
        self.splat = pg.transform.scale(splat, (64, 64))

    def avoid_mobs(self) -> None:
        for mob in self.game.mobs:
            if mob != self:
                dist = self.pos - mob.pos
                if 0 < dist.length() < AVOID_RADIUS:
                    self.acc += dist.normalize()

    def update(self) -> None:
        target_dist = self.target.pos - self.pos
        if self._target_close(target_dist):
            if random() < 0.002:
                sounds.mob_moan_sound()
            self.rot = target_dist.angle_to(Vector2(1, 0))
            self.image = pg.transform.rotate(Mob.base_image, self.rot)
            self.rect.center = self.pos
            self.acc = Vector2(1, 0).rotate(-self.rot)
            self.avoid_mobs()
            self.acc.scale_to_length(self.speed)
            self.acc += self.vel * -1
            self.vel += self.acc * self.game.dt
            self.pos += self.vel * self.game.dt
            self.pos += 0.5 * self.acc * self.game.dt ** 2
            self.hit_rect.centerx = self.pos.x
            collide_with_walls(self, self.game.walls, 'x')
            self.hit_rect.centery = self.pos.y
            collide_with_walls(self, self.game.walls, 'y')
            self.rect.center = self.hit_rect.center
        if self.health <= 0:
            sounds.mob_hit_sound()
            self.kill()
            self.game.map_img.blit(self.splat, self.pos - Vector2(32, 32))

    @staticmethod
    def _target_close(target_dist: Vector2) -> bool:
        _target_close = target_dist.length_squared() < DETECT_RADIUS ** 2
        return _target_close

    def draw_health(self) -> None:
        if self.health > 60:
            col = GREEN
        elif self.health > 30:
            col = YELLOW
        else:
            col = RED
        width = int(self.rect.width * self.health / MOB_HEALTH)
        self.health_bar = pg.Rect(0, 0, width, 7)
        if self.health < MOB_HEALTH:
            pg.draw.rect(self.image, col, self.health_bar)


class Bullet(pg.sprite.Sprite):
    def __init__(self, game: Any, pos: Vector2, direction: Vector2,
                 weapon: str) -> None:
        self._layer = BULLET_LAYER
        self.groups = game.all_sprites, game.bullets
        pg.sprite.Sprite.__init__(self, self.groups)
        self.game = game

        game_folder = path.dirname(__file__)
        img_folder = path.join(game_folder, 'img')
        blt_img_path = path.join(img_folder, BULLET_IMG)
        blt_img = pg.image.load(blt_img_path).convert_alpha()

        if weapon == 'pistol':
            self.image = blt_img
        else:
            self.image = pg.transform.scale(blt_img, (10, 10))
        self.rect = self.image.get_rect()
        self.hit_rect = self.rect
        self.pos = Vector2(pos)
        self.rect.center = pos
        # spread = uniform(-GUN_SPREAD, GUN_SPREAD)
        self.vel = direction * WEAPONS[weapon]['bullet_speed'] * uniform(0.9, 1.1)
        self.spawn_time = pg.time.get_ticks()
        self.damage = WEAPONS[weapon]['damage']

    def update(self) -> None:
        self.pos += self.vel * self.game.dt
        self.rect.center = self.pos
        if pg.sprite.spritecollideany(self, self.game.walls):
            self.kill()
        if pg.time.get_ticks() - self.spawn_time > \
                WEAPONS[self.game.player.weapon]['bullet_lifetime']:
            self.kill()


class Obstacle(pg.sprite.Sprite):
    def __init__(self, game: Any, x: int, y: int, w: int,
                 h: int) -> None:
        self.groups = game.walls
        pg.sprite.Sprite.__init__(self, self.groups)
        self.game = game
        self.rect = pg.Rect(x, y, w, h)
        self.hit_rect = self.rect
        self.x = x
        self.y = y
        self.rect.x = x
        self.rect.y = y


class MuzzleFlash(pg.sprite.Sprite):
    def __init__(self, game: Any, pos: Vector2) -> None:
        self._layer = EFFECTS_LAYER
        self.groups = game.all_sprites
        pg.sprite.Sprite.__init__(self, self.groups)
        self.game = game
        size = randint(20, 50)

        game_folder = path.dirname(__file__)
        img_folder = path.join(game_folder, 'img')
        img_path = path.join(img_folder, choice(MUZZLE_FLASHES))
        img = pg.image.load(img_path).convert_alpha()
        self.image = pg.transform.scale(img, (size, size))

        self.rect = self.image.get_rect()
        self.pos = pos
        self.rect.center = pos
        self.spawn_time = pg.time.get_ticks()

    def update(self) -> None:
        if pg.time.get_ticks() - self.spawn_time > FLASH_DURATION:
            self.kill()


class Item(pg.sprite.Sprite):
    def __init__(self, game: Any, pos: pg.math.Vector2,
                 type: str) -> None:
        self._layer = ITEMS_LAYER
        self.groups = game.all_sprites, game.items
        pg.sprite.Sprite.__init__(self, self.groups)
        self.game = game
        self.image = game.item_images[type]
        self.rect = self.image.get_rect()
        self.type = type
        self.pos = pos
        self.rect.center = pos
        self.tween = tween.easeInOutSine
        self.step = 0
        self.dir = 1

    def update(self) -> None:
        # bobbing motion
        offset = BOB_RANGE * (self.tween(self.step / BOB_RANGE) - 0.5)
        self.rect.centery = self.pos.y + offset * self.dir
        self.step += BOB_SPEED
        if self.step > BOB_RANGE:
            self.step = 0
            self.dir *= -1

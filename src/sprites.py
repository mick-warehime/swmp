import pygame as pg
from random import uniform, choice, randint, random
from typing import Any, Union
from pygame.math import Vector2
from pygame.sprite import Sprite, Group
from tilemap import collide_hit_rect
import pytweening as tween
from itertools import chain
import settings
import sounds
import images


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


class GameObject(pg.sprite.Sprite):
    """In-game object with a body for collisions and an image.
    """
    base_image: Union[pg.Surface, None] = None

    def __init__(self, image_file: str, hit_rect: pg.Rect,
                 pos: Vector2) -> None:
        self._init_base_image(image_file)

        self.image = self.base_image
        self.pos = pos
        self.rect = self.image.get_rect()
        self.rect.center = (pos.x, pos.y)

        self.hit_rect = hit_rect.copy()
        self.hit_rect.center = self.rect.center

    @classmethod
    def _init_base_image(cls, image_file: str) -> None:
        if cls.base_image is None:
            img = images.get_image(image_file)
            cls.base_image = img


class Humanoid(GameObject):
    """GameObject with health and motion. We will add more to this later."""

    def __init__(self, image_file: str, hit_rect: pg.Rect, pos: Vector2,
                 health: int) -> None:
        super(Humanoid, self).__init__(image_file, hit_rect, pos)
        self.vel = Vector2(0, 0)
        self.acc = Vector2(0, 0)
        self.rect.center = self.pos
        self.rot = 0
        self.health = health


class Player(Humanoid):
    def __init__(self, game: Any, pos: Vector2) -> None:
        super(Player, self).__init__(images.PLAYER_IMG,
                                     settings.PLAYER_HIT_RECT, pos,
                                     settings.PLAYER_HEALTH)
        self.groups = game.all_sprites
        pg.sprite.Sprite.__init__(self, self.groups)
        self.game = game

        self.last_shot = 0

        self.weapon = 'pistol'
        self.damaged = False
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

    def shoot(self) -> None:
        now = pg.time.get_ticks()
        if now - self.last_shot > settings.WEAPONS[self.weapon]['rate']:
            self.last_shot = now
            dir = Vector2(1, 0).rotate(-self.rot)
            pos = self.pos + settings.BARREL_OFFSET.rotate(-self.rot)
            self.vel = Vector2(-settings.WEAPONS[self.weapon]['kickback'],
                               0).rotate(
                -self.rot)
            for i in range(settings.WEAPONS[self.weapon]['bullet_count']):
                spread = uniform(-settings.WEAPONS[self.weapon]['spread'],
                                 settings.WEAPONS[self.weapon]['spread'])
                Bullet(self.game, pos, dir.rotate(spread), self.weapon)
                sounds.fire_weapon_sound(self.weapon)
            MuzzleFlash(self.game, pos)

    def hit(self) -> None:
        self.damaged = True

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
        if self.health > settings.PLAYER_HEALTH:
            self.health = settings.PLAYER_HEALTH


class Mob(Humanoid):
    def __init__(self, game: Any, pos: Vector2) -> None:

        super(Mob, self).__init__(images.MOB_IMG, settings.MOB_HIT_RECT, pos,
                                  settings.MOB_HEALTH)

        self.groups = game.all_sprites, game.mobs
        pg.sprite.Sprite.__init__(self, self.groups)

        self.game = game

        self.speed = choice(settings.MOB_SPEEDS)
        self.target = game.player

        splat_img = images.get_image(images.SPLAT)
        self.splat = pg.transform.scale(splat_img, (64, 64))

    def avoid_mobs(self) -> None:
        for mob in self.game.mobs:
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
        return target_dist.length_squared() < settings.DETECT_RADIUS ** 2

    def draw_health(self) -> None:
        if self.health > 60:
            col = settings.GREEN
        elif self.health > 30:
            col = settings.YELLOW
        else:
            col = settings.RED
        width = int(self.rect.width * self.health / settings.MOB_HEALTH)
        self.health_bar = pg.Rect(0, 0, width, 7)
        if self.health < settings.MOB_HEALTH:
            pg.draw.rect(self.image, col, self.health_bar)


class Bullet(pg.sprite.Sprite):
    def __init__(self, game: Any, pos: Vector2, direction: Vector2,
                 weapon: str) -> None:
        self.groups = game.all_sprites, game.bullets
        pg.sprite.Sprite.__init__(self, self.groups)
        self.game = game

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
        self.spawn_time = pg.time.get_ticks()
        self.damage = settings.WEAPONS[weapon]['damage']

    def update(self) -> None:
        self.pos += self.vel * self.game.dt
        self.rect.center = self.pos
        if pg.sprite.spritecollideany(self, self.game.walls):
            self.kill()
        if pg.time.get_ticks() - self.spawn_time > \
                settings.WEAPONS[self.game.player.weapon]['bullet_lifetime']:
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
        self._layer = settings.EFFECTS_LAYER
        self.groups = game.all_sprites
        pg.sprite.Sprite.__init__(self, self.groups)
        self.game = game
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
    def __init__(self, game: Any, pos: pg.math.Vector2, type: str) -> None:
        self._layer = settings.ITEMS_LAYER
        self.groups = game.all_sprites, game.items
        pg.sprite.Sprite.__init__(self, self.groups)
        self.game = game

        self.image = images.get_item_image(type)

        self.rect = self.image.get_rect()
        self.type = type
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

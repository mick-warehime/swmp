from typing import Callable, Dict, List, Union
import pygame as pg
from os import path

from pygame.math import Vector2

import tilemap
from model import Player, Mob, Obstacle, Item, collide_hit_rect, Timer, \
    Groups, Bullet
import view
from pygame.sprite import spritecollide, groupcollide
from random import random
import settings
import sounds

MOUSE_LEFT = 0
MOUSE_CENTER = 1
MOUSE_RIGHT = 2


def call_binding(key_id: int,
                 funcs: Dict[int, Callable[..., None]],
                 filter_list: List[int]) -> None:
    key_allowed = key_id in filter_list if filter_list else True

    if key_allowed:
        funcs[key_id]()


class Controller(object):
    def __init__(self) -> None:
        # maps keys to functions
        self.bindings: Dict[int, Callable[..., None]] = {}
        self.bindings_down: Dict[int, Callable[..., None]] = {}
        self.prev_keys: List[int] = [0] * len(pg.key.get_pressed())
        self.mouse_bindings: Dict[int, Callable[..., None]] = {}

    # calls this function every frame when the key is held down
    def bind(self, key: int, binding: Callable[..., None]) -> None:
        self.bindings[key] = binding

    # calls this function on frames when this becomes pressed
    def bind_down(self, key: int, binding: Callable[..., None]) -> None:
        self.bindings_down[key] = binding

    # calls this function every frame when the mouse button is held down
    def bind_mouse(self, key: int, binding: Callable[..., None]) -> None:
        self.mouse_bindings[key] = binding

    def handle_input(self, only_handle: Union[List[int], None] = None) -> None:

        if only_handle is None:
            only_handle = []

        keys = pg.key.get_pressed()
        mouse = pg.mouse.get_pressed()
        if any(keys) or any(mouse):
            for key_id in self.bindings:
                if keys[key_id]:
                    call_binding(key_id,
                                 self.bindings,
                                 only_handle)

            for mouse_id in self.mouse_bindings:
                if mouse[mouse_id]:
                    call_binding(mouse_id,
                                 self.mouse_bindings,
                                 only_handle)

            for key_id in self.bindings_down:
                # only press if key was not down last frame
                if self.prev_keys[key_id]:
                    continue
                if keys[key_id]:
                    call_binding(key_id,
                                 self.bindings_down,
                                 only_handle)

        self.prev_keys = list(keys)


class DungeonController(Controller):
    def __init__(self,
                 screen: pg.Surface,
                 map_file: str) -> None:
        super(DungeonController, self).__init__()

        self.screen = screen

        # initialize all variables and do all the setup for a new game
        self.groups = Groups()

        self.clock = pg.time.Clock()
        self.dt = 0

        self.playing = True

        self.init_map(map_file)

        self.camera = tilemap.Camera(self.map.width, self.map.height)

        self.init_view()

        self.init_controls()

    def init_map(self, map_file: str) -> None:

        game_folder = path.dirname(__file__)
        map_folder = path.join(game_folder, 'maps')

        # init_map
        self.map = tilemap.TiledMap(path.join(map_folder, map_file))
        self.map_img = self.map.make_map()
        self.map.rect = self.map_img.get_rect()

        timer = Timer(self)
        for tile_object in self.map.tmxdata.objects:
            obj_center = Vector2(tile_object.x + tile_object.width / 2,
                                 tile_object.y + tile_object.height / 2)
            if tile_object.name == 'player':
                pos = Vector2(obj_center.x, obj_center.y)
                self.player = Player(self.groups, timer, pos)
            if tile_object.name == 'zombie':
                pos = Vector2(obj_center.x, obj_center.y)
                Mob(pos, self.groups, timer, self.map_img, self.player)
            if tile_object.name == 'wall':
                pos = Vector2(tile_object.x, tile_object.y)
                Obstacle(self.groups.walls, pos, tile_object.width,
                         tile_object.height)
            if tile_object.name in ['health', 'shotgun']:
                Item(self.groups, obj_center, tile_object.name)

    def init_view(self) -> None:
        self.view = view.DungeonView(self.screen)
        self.view.set_sprites(self.groups.all_sprites)
        self.view.set_walls(self.groups.walls)
        self.view.set_items(self.groups.items)
        self.view.set_mobs(self.groups.mobs)

    def init_controls(self) -> None:

        self.bind_down(pg.K_n, self.view.toggle_night)
        self.bind_down(pg.K_h, self.view.toggle_debug)

        # players controls
        counterclockwise = self.player.turn_counterclockwise
        self.bind(pg.K_q, counterclockwise)

        clockwise = self.player.turn_clockwise
        self.bind(pg.K_e, clockwise)

        self.bind(pg.K_LEFT, self.player.move_left)
        self.bind(pg.K_a, self.player.move_left)

        self.bind(pg.K_RIGHT, self.player.move_right)
        self.bind(pg.K_d, self.player.move_right)

        self.bind(pg.K_UP, self.player.move_up)
        self.bind(pg.K_w, self.player.move_up)

        self.bind(pg.K_DOWN, self.player.move_down)
        self.bind(pg.K_s, self.player.move_down)

        self.bind(pg.K_SPACE, self.player.shoot)
        self.bind_mouse(MOUSE_LEFT, self.player.shoot)

    def draw(self) -> None:
        pg.display.set_caption("{:.2f}".format(self.get_fps()))

        self.view.draw(self.player,
                       self.map,
                       self.map_img,
                       self.camera)

        pg.display.flip()

    def update(self) -> None:

        # needs to be called every frame to throttle max framerate
        self.dt = self.clock.tick(settings.FPS) / 1000.0

        self.handle_input()

        # update portion of the game loop
        self.groups.all_sprites.update()
        self.camera.update(self.player)

        # game over?
        if not self.groups.mobs:
            self.playing = False

        # player hits items
        items: List[Item] = spritecollide(self.player, self.groups.items,
                                          False)
        for item in items:
            full_health = self.player.health >= settings.PLAYER_HEALTH
            if item.label == 'health' and not full_health:
                item.kill()
                sounds.play(sounds.HEALTH_UP)
                self.player.add_health(settings.HEALTH_PACK_AMOUNT)
            if item.label == 'shotgun':
                item.kill()
                sounds.play(sounds.GUN_PICKUP)
                self.player.set_weapon('shotgun')

        # mobs hit player
        mobs: List[Mob] = spritecollide(self.player, self.groups.mobs, False,
                                        collide_hit_rect)
        for zombie in mobs:
            if random() < 0.7:
                sounds.player_hit_sound()
                self.player.health -= settings.MOB_DAMAGE
            zombie.vel = pg.math.Vector2(0, 0)
            if self.player.health <= 0:
                self.playing = False
        if mobs:
            self.player.hit()
            knock_back = pg.math.Vector2(settings.MOB_KNOCKBACK, 0)
            self.player.pos += knock_back.rotate(-mobs[0].rot)

        # bullets hit mobs
        hits: Dict[Mob, List[Bullet]] = groupcollide(self.groups.mobs,
                                                     self.groups.bullets,
                                                     False, True)
        for mob, bullets in hits.items():
            mob.health -= sum(bullet.damage for bullet in bullets)
            mob.vel = pg.math.Vector2(0, 0)

    def get_fps(self) -> float:
        return self.clock.get_fps()

    # the owning object needs to know this
    def dungeon_over(self) -> bool:
        return not self.playing

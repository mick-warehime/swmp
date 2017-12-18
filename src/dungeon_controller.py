from humanoid import Player, Mob, collide_hit_rect_with_rect, Humanoid
from pygame.sprite import spritecollide, groupcollide
from model import Obstacle, Item, Timer, Groups
from item_manager import ItemManager
from pygame.math import Vector2
from typing import Dict, List
from weapon import Bullet
from os import path
from random import random
import pygame as pg
import tilemap
import view
import settings
import sounds
import controller


class DungeonController(controller.Controller):
    def __init__(self,
                 screen: pg.Surface,
                 map_file: str) -> None:
        super(DungeonController, self).__init__()

        # initialize all variables and do all the setup for a new game
        self._groups = Groups()

        self._clock = pg.time.Clock()
        self.dt = 0

        self._playing = True

        self.init_map(map_file)

        self._camera = tilemap.Camera(self._map.width, self._map.height)

        self._view = view.DungeonView(screen)
        self._view.set_sprites(self._groups.all_sprites)
        self._view.set_walls(self._groups.walls)
        self._view.set_items(self._groups.items)
        self._view.set_mobs(self._groups.mobs)

        self.init_controls()

    def init_map(self, map_file: str) -> None:

        game_folder = path.dirname(__file__)
        map_folder = path.join(game_folder, 'maps')

        # init_map
        self._map = tilemap.TiledMap(path.join(map_folder, map_file))
        self._map_img = self._map.make_map()
        self._map.rect = self._map_img.get_rect()

        self._init_humanoids()

        for tile_object in self._map.tmxdata.objects:
            obj_center = Vector2(tile_object.x + tile_object.width / 2,
                                 tile_object.y + tile_object.height / 2)
            if tile_object.name == 'player':
                pos = Vector2(obj_center.x, obj_center.y)
                self.player = Player(self._groups, pos)
            if tile_object.name == 'zombie':
                pos = Vector2(obj_center.x, obj_center.y)
                Mob(pos, self._groups, self.player)
            if tile_object.name == 'wall':
                pos = Vector2(tile_object.x, tile_object.y)
                Obstacle(self._groups.walls, pos, tile_object.width,
                         tile_object.height)
            if tile_object.name in ['health', 'shotgun', 'pistol']:
                ItemManager.item(self._groups, obj_center, tile_object.name)

    def _init_humanoids(self) -> None:
        Humanoid.init_class(self._groups.walls, Timer(self))
        Player.init_class()
        Mob.init_class(self._map_img, self._groups)

    def init_controls(self) -> None:

        self.bind_down(pg.K_n, self._view.toggle_night)
        self.bind_down(pg.K_h, self._view.toggle_debug)

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
        self.bind_mouse(controller.MOUSE_LEFT, self.player.shoot)

        self.bind_down(pg.K_f, self.use_item_in_backpack)

    def draw(self) -> None:
        pg.display.set_caption("{:.2f}".format(self.get_fps()))

        self._view.draw(self.player, self._map, self._map_img, self._camera)

        pg.display.flip()

    def update(self) -> None:

        # needs to be called every frame to throttle max framerate
        self.dt = self._clock.tick(settings.FPS) / 1000.0

        clicked_hud = self.try_handle_hud()
        if not clicked_hud:
            self.handle_input()

        # update portion of the game loop
        self._groups.all_sprites.update()
        self._camera.update(self.player)

        # game over?
        if not self._groups.mobs:
            self._playing = False

        # player hits items
        items: List[Item] = spritecollide(self.player, self._groups.items,
                                          False)
        for item in items:
            if not self.player.backpack_full():
                self.player.add_item_to_backpack(item)
                item.kill()

        # mobs hit player
        mobs: List[Mob] = spritecollide(self.player, self._groups.mobs, False,
                                        collide_hit_rect_with_rect)
        for zombie in mobs:
            if random() < 0.7:
                sounds.player_hit_sound()
                self.player.increment_health(-settings.MOB_DAMAGE)
            zombie.stop_x()
            zombie.stop_y()
            if self.player.health <= 0:
                self._playing = False
        if mobs:
            knock_back = pg.math.Vector2(settings.MOB_KNOCKBACK, 0)
            self.player.pos += knock_back.rotate(-mobs[0].rot)

        # bullets hit mobs
        hits: Dict[Mob, List[Bullet]] = groupcollide(self._groups.mobs,
                                                     self._groups.bullets,
                                                     False, True)
        for mob, bullets in hits.items():
            mob.increment_health(-sum(bullet.damage for bullet in bullets))
            mob.stop_x()
            mob.stop_y()

        self.set_previous_input()

    def get_fps(self) -> float:
        return self._clock.get_fps()

    # the owning object needs to know this
    def dungeon_over(self) -> bool:
        return not self._playing

    def try_handle_hud(self) -> bool:
        pos = self.get_clicked_pos()
        if pos == controller.NOT_CLICKED:
            return False

        self._view.try_click_mod(pos)
        self._view.try_click_item(pos)

        return self._view.clicked_hud(pos)

    def use_item_in_backpack(self) -> None:
        '''use an item if the user selects an item in the backpack
        and hits the 'use' button binding. item.use is a virtual
        method implemented separately for each item/mod type.
        if item is a mod this will equip that mod at the proper
        location'''
        idx = self._view._selected_item
        if idx == view.NO_SELECTION:
            return

        used_item = False
        try:
            itm = self.player.backpack[idx]
            if isinstance(itm, Item):
                used_item = itm.use(self.player)
        except Exception as e:
            print(e)

        if used_item:
            self._view._selected_item = view.NO_SELECTION

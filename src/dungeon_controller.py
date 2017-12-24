import abilities
import mods
from humanoids import Player, Mob, collide_hit_rect_with_rect
import humanoids
from pygame.sprite import spritecollide, groupcollide
from mods import ItemObject
from model import Obstacle, Groups, GameObject, Timer, \
    DynamicObject, Waypoint
from item_manager import ItemManager
from pygame.math import Vector2
from typing import Dict, List, Tuple
from weapons import Bullet
from os import path
from random import random
import pygame as pg
import tilemap
import view
import settings
import sounds
import controller
import conflict


class DungeonController(controller.Controller):
    def __init__(self,
                 screen: pg.Surface,
                 map_file: str) -> None:
        super().__init__()

        # initialize all variables and do all the setup for a new game
        self._groups = Groups()

        self._clock = pg.time.Clock()
        self.dt = 0

        self.init_map(map_file)

        self._camera = tilemap.Camera(self._map.width, self._map.height)

        self._view = view.DungeonView(screen)
        self._view.set_groups(self._groups)

        self.init_controls()

        self._conflict = conflict.Conflict(self._groups.conflicts)

    def init_map(self, map_file: str) -> None:

        game_folder = path.dirname(__file__)
        map_folder = path.join(game_folder, 'maps')

        # init_map
        self._map = tilemap.TiledMap(path.join(map_folder, map_file))
        self._map_img = self._map.make_map()
        self._map.rect = self._map_img.get_rect()

        self._init_gameobjects()

        # ensure the player is instantiated first
        for tile_object in self._map.tmxdata.objects:
            obj_center = Vector2(tile_object.x + tile_object.width / 2,
                                 tile_object.y + tile_object.height / 2)
            if tile_object.name == tilemap.ObjectType.PLAYER:
                self.player = Player(obj_center)

        for tile_object in self._map.tmxdata.objects:
            obj_center = Vector2(tile_object.x + tile_object.width / 2,
                                 tile_object.y + tile_object.height / 2)

            is_quest_object = self.is_quest_object(tile_object.type)

            if tile_object.name == tilemap.ObjectType.ZOMBIE:
                Mob(obj_center, self.player, quest=is_quest_object)
            if tile_object.name == tilemap.ObjectType.WALL:
                pos = Vector2(tile_object.x, tile_object.y)
                Obstacle(pos, tile_object.width, tile_object.height)
            if tile_object.name in tilemap.ITEMS:
                ItemManager.item(obj_center, tile_object.name)
            if tile_object.name == tilemap.ObjectType.WAYPOINT:
                Waypoint(obj_center, self.player)

    @staticmethod
    def is_quest_object(object_type: str) -> bool:
        if not object_type:
            return False
        quest_type = tilemap.ObjectType.QUEST
        return tilemap.ObjectType(object_type) == quest_type

    def _init_gameobjects(self) -> None:
        GameObject.initialize_gameobjects(self._groups)
        timer = Timer(self)
        DynamicObject.initialize_dynamic_objects(timer)
        Mob.init_class(self._map_img)
        # Bullet.initialize_class()
        mods.initialize_classes()
        abilities.initialize_classes(timer)

    def init_controls(self) -> None:

        self.bind_down(pg.K_n, self._view.toggle_night)
        self.bind_down(pg.K_h, self._view.toggle_debug)

        # players controls
        self.bind(pg.K_LEFT, self.player.translate_left)
        self.bind(pg.K_a, self.player.translate_left)

        self.bind(pg.K_RIGHT, self.player.translate_right)
        self.bind(pg.K_d, self.player.translate_right)

        self.bind(pg.K_UP, self.player.translate_up)
        self.bind(pg.K_w, self.player.translate_up)

        self.bind(pg.K_DOWN, self.player.translate_down)
        self.bind(pg.K_s, self.player.translate_down)

        arms_ability = self.player.ability_caller(mods.ModLocation.ARMS)
        self.bind(pg.K_SPACE, arms_ability)
        self.bind_mouse(controller.MOUSE_LEFT, arms_ability)

        chest_ability = self.player.ability_caller(mods.ModLocation.CHEST)
        self.bind_down(pg.K_r, chest_ability)

        # equip / use
        self.bind_down(pg.K_e, self.use_item_in_backpack)

    def draw(self) -> None:
        pg.display.set_caption("{:.2f}".format(self.get_fps()))

        self._view.draw(self.player, self._map, self._map_img, self._camera)

        pg.display.flip()

    def update(self) -> None:

        # needs to be called every frame to throttle max framerate
        self.dt = self._clock.tick(settings.FPS) / 1000.0

        self.pass_mouse_pos_to_player()

        clicked_hud = self.try_handle_hud()
        if not clicked_hud:
            self.handle_input()

        # update portion of the game loop
        self._groups.all_sprites.update()
        self._camera.update(self.player)

        # player hits items
        items: List[ItemObject] = spritecollide(self.player,
                                                self._groups.items, False)
        for item in items:
            self.player.attempt_pickup(item)

        # mobs hit player
        mobs: List[Mob] = spritecollide(self.player, self._groups.mobs, False,
                                        collide_hit_rect_with_rect)
        for zombie in mobs:
            if random() < 0.7:
                sounds.player_hit_sound()
                self.player.increment_health(-humanoids.MOB_DAMAGE)
            zombie.stop_x()
            zombie.stop_y()
            if self.player.health <= 0:
                self._playing = False
        if mobs:
            knock_back = pg.math.Vector2(humanoids.MOB_KNOCKBACK, 0)
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
        return self._conflict.is_resolved()

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
        idx = self._view.selected_item()
        if idx == view.NO_SELECTION:
            return

        if idx + 1 >= len(self.player.backpack):
            item_in_backpack = self.player.backpack[idx]
            self.player.equip(item_in_backpack)
            self._view.set_selected_item(view.NO_SELECTION)

    def pass_mouse_pos_to_player(self) -> None:
        mouse_pos = self.abs_mouse_pos()
        self.player.set_mouse_pos(mouse_pos)

    # mouse coordinates are relative to the camera
    # most other coordinates are relative to the map
    def abs_mouse_pos(self) -> Tuple[int, int]:
        mouse_pos = pg.mouse.get_pos()
        camera_pos = self._camera.camera
        abs_mouse_x = mouse_pos[0] - camera_pos[0]
        abs_mouse_y = mouse_pos[1] - camera_pos[1]
        return (abs_mouse_x, abs_mouse_y)

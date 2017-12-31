from random import random
from typing import Dict, List, Tuple

import pygame as pg
from pygame.math import Vector2
from pygame.sprite import spritecollide, groupcollide

import abilities
import controller
import mods
import settings
import sounds
import tilemap
import view

from creatures.mobs import Mob
from creatures.humanoids import collide_hit_rect_with_rect
from creatures.players import Player
from items.item_manager import ItemManager
from model import Obstacle, Groups, GameObject, Timer, \
    DynamicObject, Waypoint, Group, ConflictGroups
from mods import ItemObject
from weapons import Projectile


class DungeonController(controller.Controller):
    def __init__(self, map_file: str) -> None:
        super().__init__()

        # initialize all variables and do all the setup for a new game
        self._groups = Groups()

        self._clock = pg.time.Clock()
        self.dt = 0

        # init_map
        self._map = tilemap.TiledMap(map_file)
        self._init_map_objects()

        self._camera = tilemap.Camera(self._map.width, self._map.height)

        self._view = view.DungeonView(self._screen)
        self._view.set_groups(self._groups)

        self.init_controls()

    def _init_map_objects(self) -> None:
        # provide the group containers for the map objects
        self._init_gameobjects()
        self._conflicts = ConflictGroups()

        # initialize the player on the map before anything else
        for obj in self._map.objects:
            if obj.type == tilemap.ObjectType.PLAYER:
                self.player = Player(obj.center)

        assert self.player is not None, 'no player found in map'

        for obj in self._map.objects:
            conflict_group = self._get_conflict(obj.conflict)
            if obj.type == tilemap.ObjectType.ZOMBIE:
                Mob(obj.center, self.player, conflict_group)
            if obj.type == tilemap.ObjectType.WALL:
                pos = Vector2(obj.x, obj.y)
                Obstacle(pos, obj.width, obj.height)
            if obj.type in tilemap.ITEMS:
                ItemManager.item(obj.center, obj.type)
            if obj.type == tilemap.ObjectType.WAYPOINT:
                Waypoint(obj.center, self.player, conflict_group)

    def _get_conflict(self, conflict_name: str) -> Group:
        if conflict_name == tilemap.NOT_CONFLICT:
            return None
        return self._conflicts.get_group(conflict_name)

    def _init_gameobjects(self) -> None:
        GameObject.initialize_gameobjects(self._groups)
        timer = Timer(self)
        DynamicObject.initialize_dynamic_objects(timer)
        Mob.init_class(self._map.img)
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

        self.bind_down(pg.K_b, self.toggle_hide_backpack)

        # equip / use
        self.bind_down(pg.K_e, self.try_equip)

    def draw(self) -> None:
        pg.display.set_caption("{:.2f}".format(self.get_fps()))

        self._view.draw(self.player, self._map, self._map.img, self._camera)

        self._view.draw_conflicts(self._conflicts)

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

        # obs hit player
        hitters: List[Mob] = spritecollide(self.player, self._groups.mobs,
                                           False, collide_hit_rect_with_rect)
        for zombie in hitters:
            if random() < 0.7:
                sounds.player_hit_sound()
                self.player.increment_health(-Mob.damage)
            zombie.stop_x()
            zombie.stop_y()

        if hitters:
            knock_back = pg.math.Vector2(Mob.knockback, 0)
            self.player.pos += knock_back.rotate(-hitters[0].rot)

        # enemy projectiles hit player
        projectiles: List[Projectile] = spritecollide(
            self.player, self._groups.enemy_projectiles, True,
            collide_hit_rect_with_rect)

        for projectile in projectiles:
            self.player.increment_health(-projectile.damage)

        # bullets hit hitting_mobs
        hits: Dict[Mob, List[Projectile]] = groupcollide(self._groups.mobs,
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
    def should_exit(self) -> bool:
        return self._conflicts.any_resolved_conflict()

    def game_over(self) -> bool:
        return self.player.health <= 0

    def try_handle_hud(self) -> bool:
        pos = self.get_clicked_pos()
        if pos == controller.NOT_CLICKED:
            return False

        self._view.try_click_mod(pos)
        self._view.try_click_item(pos)

        return self._view.clicked_hud(pos)

    def try_equip(self) -> None:
        self.equip_mod_in_backpack()
        self.unequip_mod()

    def equip_mod_in_backpack(self) -> None:
        '''equip amod if the user selects it in the backpack and hits the
        'equip' button binding.'''
        idx = self._view.selected_item()
        if idx == view.NO_SELECTION:
            return

        backpack = self.player.backpack
        if backpack.slot_occupied(idx):
            self.player.equip(backpack[idx])
            self._view.set_selected_item(view.NO_SELECTION)

    def unequip_mod(self) -> None:
        '''unequip amod if the user selects it in the hud and hits the
                'equip' button binding.'''
        location = self._view.selected_mod()
        if location == view.NO_SELECTION:
            return

        self.player.unequip(location)

    def pass_mouse_pos_to_player(self) -> None:
        mouse_pos = self.abs_mouse_pos()
        self.player.set_mouse_pos(mouse_pos)

    # mouse coordinates are relative to the camera
    # most other coordinates are relative to the map
    def abs_mouse_pos(self) -> Tuple[int, int]:
        mouse_pos = pg.mouse.get_pos()
        camera_pos = self._camera.rect
        abs_mouse_x = mouse_pos[0] - camera_pos[0]
        abs_mouse_y = mouse_pos[1] - camera_pos[1]
        return (abs_mouse_x, abs_mouse_y)

    def toggle_hide_backpack(self) -> None:
        self._view.toggle_hide_backpack()

    def resolved_conflict_index(self) -> int:
        return self._conflicts.resolved_conflict()

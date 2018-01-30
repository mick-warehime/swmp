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
from creatures.humanoids import collide_hit_rect_with_rect
from creatures.enemies import Enemy, mob_data, quest_mob_data
from creatures.players import Player
from data.constructors import ItemManager
from items import ItemObject
from model import Obstacle, Groups, GameObject, Timer, \
    DynamicObject, Group, ConflictGroups
from waypoints import Waypoint
from projectiles import Projectile


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

        self._init_controls()

        self.teleported = False

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
                if conflict_group is not None:
                    data = quest_mob_data.add_quest_group(conflict_group)
                else:
                    data = mob_data
                Enemy(obj.center, self.player, data)
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
        abilities.initialize_classes(timer)
        Enemy.init_class(self._map.img)

    def init_controls(self) -> None:

        self.bind_on_press(pg.K_n, self._view.toggle_night)
        self.bind_on_press(pg.K_h, self._view.toggle_debug)

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
        self.bind_on_press(pg.K_r, chest_ability)

        self.bind_on_press(pg.K_b, self.toggle_hide_backpack)

        # equip / use
        self.bind_on_press(pg.K_e, self.try_equip)

        self.bind_on_press(pg.K_t, self.teleport)

    def draw(self) -> None:
        pg.display.set_caption("{:.2f}".format(self.get_fps()))

        self._view.draw(self.player, self._map, self._map.img, self._camera)

        self._view.draw_conflicts(self._conflicts)

        pg.display.flip()

    def update(self) -> None:

        # needs to be called every frame to throttle max framerate
        self.dt = self._clock.tick(settings.FPS) / 1000.0

        self._pass_mouse_pos_to_player()

        clicked_hud = self._try_handle_hud()
        if not clicked_hud:
            self.handle_input()

        # update portion of the game loop
        self._groups.all_sprites.update()
        self._camera.update(self.player)

        self._handle_collisions()

        self.set_previous_input()

    def _handle_collisions(self) -> None:
        # player hits items
        items: List[ItemObject] = spritecollide(self.player,
                                                self._groups.items, False)
        for item in items:
            self.player.inventory.attempt_pickup(item)

        # obs hit player
        hitters: List[Enemy] = spritecollide(self.player, self._groups.enemies,
                                             False, collide_hit_rect_with_rect)
        for zombie in hitters:
            if random() < 0.7:
                sounds.player_hit_sound()
                self.player.status.increment_health(-zombie.damage)
            zombie.motion.stop()
        if hitters:
            amount = max(hitter.knockback for hitter in hitters)
            knock_back = pg.math.Vector2(amount, 0)
            self.player.pos += knock_back.rotate(-hitters[0].motion.rot)

        # enemy projectiles hit player
        projectiles: List[Projectile] = spritecollide(
            self.player, self._groups.enemy_projectiles, True,
            collide_hit_rect_with_rect)
        for projectile in projectiles:
            self.player.status.increment_health(-projectile.damage)

        # bullets hit hitting_mobs
        hits: Dict[Enemy, List[Projectile]] = groupcollide(
            self._groups.enemies, self._groups.bullets, False, True)
        for mob, bullets in hits.items():
            mob.status.increment_health(
                -sum(bullet.damage for bullet in bullets))
            mob.motion.stop()

    def get_fps(self) -> float:
        return self._clock.get_fps()

    # the owning object needs to know this
    def should_exit(self) -> bool:
        conflict_resolved = self._conflicts.any_resolved_conflict()
        return conflict_resolved and self.teleported

    def game_over(self) -> bool:
        return self.player.status.is_dead

    def resolved_conflict_index(self) -> int:
        return self._conflicts.resolved_conflict()

    def _init_controls(self) -> None:

        self.bind_on_press(pg.K_n, self._view.toggle_night)
        self.bind_on_press(pg.K_h, self._view.toggle_debug)

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
        self.bind_on_press(pg.K_r, chest_ability)

        self.bind_on_press(pg.K_b, self._toggle_hide_backpack)

        # equip / use
        self.bind_on_press(pg.K_e, self._try_equip)

        self.bind_on_press(pg.K_t, self._teleport)

    def _try_handle_hud(self) -> bool:
        pos = self.get_clicked_pos()
        if pos == controller.NOT_CLICKED:
            return False

        self._view.try_click_mod(pos)
        self._view.try_click_item(pos)

        return self._view.clicked_hud(pos)

    def _try_equip(self) -> None:
        self._equip_mod_in_backpack()
        self._unequip_mod()

    def _equip_mod_in_backpack(self) -> None:
        '''equip amod if the user selects it in the backpack and hits the
        'equip' button binding.'''
        idx = self._view.selected_item()
        if idx == view.NO_SELECTION:
            return

        backpack = self.player.inventory.backpack
        if backpack.slot_occupied(idx):
            self.player.inventory.equip(backpack[idx])
            self._view.set_selected_item(view.NO_SELECTION)

    def _unequip_mod(self) -> None:
        '''unequip amod if the user selects it in the hud and hits the
                'equip' button binding.'''
        location = self._view.selected_mod()
        if location == view.NO_SELECTION:
            return

        self.player.inventory.unequip(location)

    def _pass_mouse_pos_to_player(self) -> None:
        mouse_pos = self._abs_mouse_pos()
        self.player.set_mouse_pos(mouse_pos)

    # mouse coordinates are relative to the camera
    # most other coordinates are relative to the map
    def _abs_mouse_pos(self) -> Tuple[int, int]:
        mouse_pos = pg.mouse.get_pos()
        camera_pos = self._camera.rect
        abs_mouse_x = mouse_pos[0] - camera_pos[0]
        abs_mouse_y = mouse_pos[1] - camera_pos[1]
        return (abs_mouse_x, abs_mouse_y)

    def _toggle_hide_backpack(self) -> None:
        self._view.toggle_hide_backpack()

    def _teleport(self) -> None:
        self.teleported = True

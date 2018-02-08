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
from creatures.enemies import Enemy
from creatures.players import Player
from data import constructors
from items import ItemObject
from model import Obstacle, Groups, GameObject, Timer, DynamicObject, Group, \
    ConflictGroups
from projectiles import Projectile


class Dungeon(object):
    """Stores and updates GameObjects in a dungeon map."""

    def __init__(self, map_file: str) -> None:
        super().__init__()

        # initialize all variables and do all the setup for a new game
        self.groups = Groups()
        self.conflicts: ConflictGroups = None

        self._clock = pg.time.Clock()

        # init_map
        self.map = tilemap.TiledMap(map_file)
        self._init_map_objects()

    def _init_map_objects(self) -> None:
        # provide the group containers for the map objects
        self._init_gameobjects()
        self.conflicts = ConflictGroups()

        # initialize the player on the map before anything else
        for obj in self.map.objects:
            if obj.type == tilemap.ObjectType.PLAYER:
                self.player = Player(obj.center)

        assert self.player is not None, 'no player found in map'

        for obj in self.map.objects:
            conflict_group = self._get_conflict(obj.conflict)

            if obj.type == tilemap.ObjectType.PLAYER:
                continue
            if obj.type == tilemap.ObjectType.WALL:
                pos = Vector2(obj.x, obj.y)
                Obstacle(pos, obj.width, obj.height)
                continue

            constructors.build_map_object(obj.type, obj.center, self.player,
                                          conflict_group)

    def _get_conflict(self, conflict_name: str) -> Group:
        if conflict_name == tilemap.NOT_CONFLICT:
            return None
        return self.conflicts.get_group(conflict_name)

    def _init_gameobjects(self) -> None:
        GameObject.initialize_gameobjects(self.groups)
        timer = Timer(self._clock)
        DynamicObject.initialize_dynamic_objects(timer)
        abilities.initialize_classes(timer)
        Enemy.init_class(self.map.img)

    def update(self) -> None:

        # needs to be called every frame to throttle max framerate
        self._clock.tick(settings.FPS)

        self.groups.all_sprites.update()

        self._handle_collisions()

    def _handle_collisions(self) -> None:
        # player hits items
        items: List[ItemObject] = spritecollide(self.player, self.groups.items,
                                                False)
        for item in items:
            self.player.inventory.attempt_pickup(item)

        # obs hit player
        hitters: List[Enemy] = spritecollide(self.player, self.groups.enemies,
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
            self.player, self.groups.enemy_projectiles, True,
            collide_hit_rect_with_rect)
        for projectile in projectiles:
            self.player.status.increment_health(-projectile.damage)

        # bullets hit hitting_mobs
        hits: Dict[Enemy, List[Projectile]] = groupcollide(
            self.groups.enemies, self.groups.bullets, False, True)
        for mob, bullets in hits.items():
            mob.status.increment_health(
                -sum(bullet.damage for bullet in bullets))
            mob.motion.stop()

    def get_fps(self) -> float:
        return self._clock.get_fps()


class DungeonController(controller.Controller):
    def __init__(self, map_file: str) -> None:
        super().__init__()

        self._dungeon = Dungeon(map_file)
        self.player = self._dungeon.player

        self._view = view.DungeonView(self._screen)
        self._view.set_groups(self._dungeon.groups)
        self._view.set_camera_range(self._dungeon.map.width,
                                    self._dungeon.map.height)

        self._init_controls()

        self._teleported = False

    def draw(self) -> None:
        pg.display.set_caption("{:.2f}".format(self.get_fps()))

        self._view.draw(self.player, self._dungeon.map)
        self._view.draw_conflicts(self._dungeon.conflicts)

        pg.display.flip()

    def update(self) -> None:

        self._pass_mouse_pos_to_player()

        clicked_hud = self._try_handle_hud()
        if not clicked_hud:
            self.keyboard.handle_input()

        self._dungeon.update()

        self.keyboard.set_previous_input()

    def get_fps(self) -> float:
        return self._dungeon.get_fps()

    # the owning object needs to know this
    def should_exit(self) -> bool:
        conflict_resolved = self._dungeon.conflicts.any_resolved_conflict()
        return conflict_resolved and self._teleported

    def game_over(self) -> bool:
        return self.player.status.is_dead

    def resolved_conflict_index(self) -> int:
        return self._dungeon.conflicts.resolved_conflict()

    def _init_controls(self) -> None:

        self.keyboard.bind_on_press(pg.K_n, self._view.toggle_night)
        self.keyboard.bind_on_press(pg.K_h, self._view.toggle_debug)

        # players controls
        player = self.player
        self.keyboard.bind(pg.K_LEFT, player.translate_left)
        self.keyboard.bind(pg.K_a, player.translate_left)

        self.keyboard.bind(pg.K_RIGHT, player.translate_right)
        self.keyboard.bind(pg.K_d, player.translate_right)

        self.keyboard.bind(pg.K_UP, player.translate_up)
        self.keyboard.bind(pg.K_w, player.translate_up)

        self.keyboard.bind(pg.K_DOWN, player.translate_down)
        self.keyboard.bind(pg.K_s, player.translate_down)

        arms_ability = player.ability_caller(mods.ModLocation.ARMS)
        self.keyboard.bind(pg.K_SPACE, arms_ability)
        self.keyboard.bind_mouse(controller.MOUSE_LEFT, arms_ability)

        chest_ability = player.ability_caller(mods.ModLocation.CHEST)
        self.keyboard.bind_on_press(pg.K_r, chest_ability)

        self.keyboard.bind_on_press(pg.K_b, self._toggle_hide_backpack)

        # equip / use
        self.keyboard.bind_on_press(pg.K_e, self._try_equip)

        self.keyboard.bind_on_press(pg.K_t, self._teleport)

    def _try_handle_hud(self) -> bool:
        if not self.keyboard.mouse_just_clicked:
            return False
        pos = self.keyboard.mouse_pos

        self._view.try_click_mod(pos)
        self._view.try_click_item(pos)

        return self._view.clicked_hud(pos)

    def _try_equip(self) -> None:
        self._equip_mod_in_backpack()
        self._unequip_mod()

    def _equip_mod_in_backpack(self) -> None:
        """equip a mod if the user selects it in the backpack and hits the
        'equip' button binding."""
        idx = self._view.selected_item()
        if idx == view.NO_SELECTION:
            return

        backpack = self.player.inventory.backpack
        if backpack.slot_occupied(idx):
            self.player.inventory.equip(backpack[idx])
            self._view.set_selected_item(view.NO_SELECTION)

    def _unequip_mod(self) -> None:
        """unequip a mod if the user selects it in the hud and hits the 'equip'
         button binding."""
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
        camera_pos = self._view.camera.rect
        abs_mouse_x = mouse_pos[0] - camera_pos[0]
        abs_mouse_y = mouse_pos[1] - camera_pos[1]
        return abs_mouse_x, abs_mouse_y

    def _toggle_hide_backpack(self) -> None:
        self._view.toggle_hide_backpack()

    def _teleport(self) -> None:
        self._teleported = True

from random import random
from typing import Dict, List, Tuple, Set

import pygame as pg
from pygame.sprite import spritecollide, groupcollide

import controllers.base
import model
import mods
import tilemap
from controllers import keyboards
from creatures.enemies import Enemy
from creatures.humanoids import collide_hit_rect_with_rect, HumanoidData
from creatures.players import Player
from data import constructors
from items import ItemObject
from projectiles import Projectile
from quests.resolutions import Resolution, RequiresTeleport
from view import dungeon_view, sounds


class Dungeon(model.GroupsAccess):
    """Stores and updates GameObjects in a dungeon map."""

    def __init__(self, map_file: str) -> None:

        # init_map
        self.map = tilemap.TiledMap(map_file)
        self.labeled_sprites: Dict[str, Set[model.GameObject]] = {}
        self._init_map_objects()

    def _init_map_objects(self) -> None:

        # initialize the player on the map before anything else
        for obj in self.map.objects:
            if obj.type == tilemap.ObjectType.PLAYER:
                self.player = Player(obj.center)

        assert self.player is not None, 'no player found in map'

        builder = constructors.build_map_object
        for obj in self.map.objects:

            if obj.type == tilemap.ObjectType.PLAYER:
                game_obj = self.player
            else:
                dims = (obj.width, obj.height)
                game_obj = builder(obj.type, obj.center, self.player, dims)
            # TODO(dvirk): Ideally this should be handled outside the scope of
            # Dungeon. Perhaps this whole method should be handled outside.
            for label in obj.labels:
                if label not in self.labeled_sprites:
                    self.labeled_sprites[label] = {game_obj}
                else:
                    self.labeled_sprites[label].add(game_obj)

    def update(self) -> None:

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


class DungeonController(controllers.base.Controller):
    """Manages interactions between a Dungeon, DungeonView, Resolutions, and
     user.
     """

    def __init__(self, dungeon: Dungeon,
                 resolutions: List[Resolution]) -> None:
        super().__init__()

        self._dungeon = dungeon

        self._view = dungeon_view.DungeonView()
        self._view.set_camera_range(self._dungeon.map.width,
                                    self._dungeon.map.height)

        self._teleport_resolutions: List[RequiresTeleport] = None
        self._teleport_resolutions = [res for res in resolutions if
                                      isinstance(res, RequiresTeleport)]

        self._init_controls(self._dungeon.player)

    def set_player_data(self, data: HumanoidData) -> None:
        self._dungeon.player.data = data

    def draw(self) -> None:

        self._view.draw_teleport_text = any(
            res.can_resolve for res in self._teleport_resolutions)
        self._view.draw(self._dungeon.player, self._dungeon.map)

        pg.display.flip()

    def update(self) -> None:

        self._pass_mouse_pos_to_player()

        if self._hud_just_clicked():
            self._handle_hud()
            self.keyboard.handle_input(['none allowed'])
        else:
            self.keyboard.handle_input()

        self._dungeon.update()

    def _hud_just_clicked(self) -> bool:
        hud_clicked = self.keyboard.mouse_just_clicked
        if hud_clicked:
            hud_clicked &= self._view.hud_collide_point(
                self.keyboard.mouse_pos)
        return hud_clicked

    def _init_controls(self, player: Player) -> None:

        self.keyboard.bind_on_press(pg.K_n, self._view.toggle_night)
        self.keyboard.bind_on_press(pg.K_h, self._view.toggle_debug)

        # players controls
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
        self.keyboard.bind_mouse(keyboards.MOUSE_LEFT, arms_ability)

        chest_ability = player.ability_caller(mods.ModLocation.CHEST)
        self.keyboard.bind_on_press(pg.K_r, chest_ability)

        self.keyboard.bind_on_press(pg.K_b, self._toggle_hide_backpack)

        # equip / use
        self.keyboard.bind_on_press(pg.K_e, self._try_equip)

        self.keyboard.bind_on_press(pg.K_t, self._teleport)

    def _handle_hud(self) -> None:
        self._view.try_click_hud(self.keyboard.mouse_pos)

    def _try_equip(self) -> None:
        self._equip_mod_in_backpack()
        self._unequip_mod()

    def _equip_mod_in_backpack(self) -> None:
        """equip a mod if the user selects it in the backpack and hits the
        'equip' button binding."""
        idx = self._view.selected_item()
        if idx == dungeon_view.NO_SELECTION:
            return

        inventory = self._dungeon.player.inventory
        if inventory.backpack.slot_occupied(idx):
            inventory.equip(inventory.backpack[idx])
            self._view.set_selected_item(dungeon_view.NO_SELECTION)

    def _unequip_mod(self) -> None:
        """unequip a mod if the user selects it in the hud and hits the 'equip'
         button binding."""
        location = self._view.selected_mod()
        if location == dungeon_view.NO_SELECTION:
            return

        self._dungeon.player.inventory.unequip(location)

    def _pass_mouse_pos_to_player(self) -> None:
        mouse_pos = self._abs_mouse_pos()
        self._dungeon.player.set_mouse_pos(mouse_pos)

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

    # Ensures that gameobjects are removed from Groups once the controller
    # is no longer used.
    def __del__(self) -> None:
        self._dungeon.groups.empty()
        del self

    def _teleport(self) -> None:
        for res in self._teleport_resolutions:
            res.toggle_teleport()

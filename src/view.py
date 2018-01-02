from typing import List, Tuple
import pygame as pg
from pygame.math import Vector2
from pygame.sprite import Sprite

import images
import mods
import settings
from creatures.players import Player
from hud import HUD
from model import Groups, ConflictGroups
from tilemap import Camera, TiledMap
from draw_utils import draw_text

NO_SELECTION = -1


class DungeonView(object):
    def __init__(self, screen: pg.Surface) -> None:

        self._screen = screen
        dim_screen = pg.Surface(screen.get_size()).convert_alpha()
        dim_screen.fill((0, 0, 0, 180))

        # HUD size & location
        self._hud = HUD(self._screen)

        self._draw_debug = False
        self._night = False

        self._fog = pg.Surface((settings.WIDTH, settings.HEIGHT))
        self._fog.fill(settings.NIGHT_COLOR)

        # lighting effect for night mode
        self._light_mask = images.get_image(images.LIGHT_MASK)
        self._light_rect = self._light_mask.get_rect()

        self._groups = None

        self.title_font = images.get_font(images.ZOMBIE_FONT)

    def set_groups(self, groups: Groups) -> None:
        self._groups = groups

    def draw(self,
             player: Player,
             map: TiledMap,
             map_img: pg.Surface,
             camera: Camera) -> None:

        self._screen.blit(map_img, camera.apply(map))

        for sprite in self._groups.all_sprites:
            self._draw_sprite(sprite, camera)

        if self._draw_debug:
            self._draw_debug_rects(camera)

        if self._night:
            self.render_fog(player, camera)

        # draw hud on top of everything
        self._hud.draw(player)

    def _draw_sprite(self, sprite: Sprite, camera: Camera)->None:
        image = sprite.image
        rect = image.get_rect().copy()
        new_center = Vector2(sprite.pos)
        new_center.x += camera.rect.topleft[0]
        new_center.y += camera.rect.topleft[1]
        rect.center = new_center
        self._screen.blit(image, rect)

    def _draw_debug_rects(self, camera: Camera) -> None:
        for sprite in self._groups.all_sprites:
            if hasattr(sprite, 'hit_rect'):
                rect = sprite.hit_rect
            else:
                rect = sprite.rect
            sprite_camera = camera.apply_rect(rect)
            pg.draw.rect(self._screen, settings.CYAN, sprite_camera, 1)
        for obstacle in self._groups.walls:
            assert obstacle not in self._groups.all_sprites
            sprite_camera = camera.apply_rect(obstacle.rect)
            pg.draw.rect(self._screen, settings.CYAN, sprite_camera, 1)

    def render_fog(self, player: Player, camera: Camera) -> None:
        # draw the light mask (gradient) onto fog image
        self._fog.fill(settings.NIGHT_COLOR)
        self._light_rect.center = camera.apply(player).center
        self._fog.blit(self._light_mask, self._light_rect)
        self._screen.blit(self._fog, (0, 0), special_flags=pg.BLEND_MULT)

    def toggle_debug(self) -> None:
        self._draw_debug = not self._draw_debug

    def toggle_night(self) -> None:
        self._night = not self._night

    def try_click_mod(self, pos: Tuple[int, int]) -> None:
        rects = [self._hud.mod_rects[l] for l in mods.ModLocation]
        index = self.clicked_rect_index(rects, pos)
        if index == self.selected_mod:
            self._hud.selected_mod = NO_SELECTION
        else:
            self._hud.selected_mod = index

    def try_click_item(self, pos: Tuple[int, int]) -> None:
        index = self.clicked_rect_index(self._hud.backpack_rects, pos)
        if index == self._hud.selected_item:
            self._hud.selected_item = NO_SELECTION
        else:
            self._hud.selected_item = index

    def clicked_rect_index(self, rects: List[pg.Rect],
                           pos: Tuple[int, int]) -> int:

        x, y = pos
        for idx, r in enumerate(rects):
            if r.collidepoint(x, y):
                return idx
        return NO_SELECTION

    def clicked_hud(self, pos: Tuple[int, int]) -> bool:
        return self._hud.clicked_hud(pos)

    def selected_item(self) -> int:
        return self._hud.selected_item

    def selected_mod(self) -> mods.ModLocation:
        if self._hud.selected_mod == NO_SELECTION:
            return NO_SELECTION

        locs = [l for l in mods.ModLocation]
        return locs[self._hud.selected_mod]

    def set_selected_item(self, idx: int) -> None:
        self._hud.selected_item = idx

    def toggle_hide_backpack(self) -> None:
        self._hud.toggle_hide_backpack()

    def draw_conflicts(self, conflictgroups: ConflictGroups) -> None:
        conflicts = conflictgroups.conflicts
        for idx, conflict_name in enumerate(conflicts.keys()):
            conflict = conflicts[conflict_name]
            conflict_str = '%d- %s' % (idx + 1, conflict.text_rep())
            color = settings.RED
            if conflict.resolved:
                color = settings.GREEN
            draw_text(self._screen, conflict_str, self.title_font,
                      16, color, 10, 10 + 16 * idx)

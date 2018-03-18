from typing import List, Tuple

import pygame as pg
from pygame.math import Vector2
from pygame.rect import Rect
from pygame.sprite import Sprite

import model
import mods
import settings
from creatures.players import Player
from tilemap import TiledMap
from view import draw_utils
from view import images
from view.camera import Camera
from view.draw_effects import DrawEffect, DrawDebugRects, DrawText
from view.draw_utils import rect_on_screen
from view.hud import HUD
from view.screen import ScreenAccess

NO_SELECTION = -1


class DungeonView(model.GroupsAccess, ScreenAccess):
    def __init__(self) -> None:
        super().__init__()

        dim_screen = pg.Surface(self.screen.get_size()).convert_alpha()
        dim_screen.fill((0, 0, 0, 180))

        self.camera: Camera = Camera(800, 600)
        DrawEffect.set_camera(self.camera)

        self._debug_drawer = DrawDebugRects()
        self._teleport_text_drawer = DrawText('Press T to continue')

        self._hud = HUD()

        self._draw_debug = False
        self._night = False
        self.draw_teleport_text = False

        self._fog = pg.Surface((settings.WIDTH, settings.HEIGHT))
        self._fog.fill(settings.NIGHT_COLOR)

        # lighting effect for night mode
        self._light_mask = images.get_image(images.LIGHT_MASK)
        self._light_rect = self._light_mask.get_rect()

        self.title_font = images.get_font(images.ZOMBIE_FONT)

    def set_camera_range(self, width: int, height: int) -> None:
        x, y = self.camera.rect.x, self.camera.rect.y
        self.camera.rect = Rect(x, y, width, height)

    def draw(self, player: Player, tile_map: TiledMap) -> None:

        self.camera.update(player)

        self.screen.blit(tile_map.img, self.camera.get_shifted_rect(tile_map))

        for sprite in self.groups.all_sprites:
            self._draw_sprite(sprite)

        if self._draw_debug:
            self._debug_drawer.draw()

        if self._night:
            self.render_fog(player)

        if self.draw_teleport_text:
            self._teleport_text_drawer.draw()

        # draw hud on top of everything
        self._hud.draw(player)

    def _draw_sprite(self, sprite: Sprite) -> None:
        image = sprite.image
        rect = image.get_rect().copy()
        new_center = Vector2(sprite.pos)
        new_center.x += self.camera.rect.topleft[0]
        new_center.y += self.camera.rect.topleft[1]
        rect.center = new_center

        if rect_on_screen(self.screen, rect):
            self.screen.blit(image, rect)

    def render_fog(self, player: Player) -> None:
        # draw the light mask (gradient) onto fog image
        self._fog.fill(settings.NIGHT_COLOR)
        self._light_rect.center = self.camera.get_shifted_rect(player).center
        self._fog.blit(self._light_mask, self._light_rect)
        self.screen.blit(self._fog, (0, 0), special_flags=pg.BLEND_MULT)

    def toggle_debug(self) -> None:
        self._draw_debug = not self._draw_debug

    def toggle_night(self) -> None:
        self._night = not self._night

    def try_click_hud(self, pos: Tuple[int, int]) -> None:
        self._try_click_mod(pos)
        self._try_click_item(pos)

    def _try_click_mod(self, pos: Tuple[int, int]) -> None:
        rects = [self._hud.mod_rects[l] for l in mods.ModLocation]
        index = self.clicked_rect_index(rects, pos)
        if index == self.selected_mod:
            self._hud.selected_mod = NO_SELECTION
        else:
            self._hud.selected_mod = index

    def _try_click_item(self, pos: Tuple[int, int]) -> None:
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

    def hud_collide_point(self, pos: Tuple[int, int]) -> bool:
        return self._hud.collide_point(pos)

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

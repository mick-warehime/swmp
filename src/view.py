from typing import List, Tuple
import settings
import pygame as pg
from humanoids import Mob, Player
from model import Groups
from tilemap import Camera, TiledMap
import images
import mods

from hud import HUD
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

        # TODO(dvirk): This should not have to be instantiated here,
        # but assigned to the view before the draw method is called.
        self._groups = Groups()

    def set_groups(self, groups: Groups) -> None:
        self._groups = groups

    def draw(self,
             player: Player,
             map: TiledMap,
             map_img: pg.Surface,
             camera: Camera) -> None:

        self._screen.blit(map_img, camera.apply(map))

        for sprite in self._groups.all_sprites:
            if isinstance(sprite, Mob):
                sprite.draw_health()
            self._screen.blit(sprite.image, camera.apply(sprite))
            if self._draw_debug and hasattr(sprite, 'hit_rect'):
                sprite_camera = camera.apply_rect(sprite.hit_rect)
                pg.draw.rect(self._screen, settings.CYAN, sprite_camera, 1)
        if self._draw_debug:
            for wall in self._groups.walls:
                wall_camera = camera.apply_rect(wall.rect)
                pg.draw.rect(self._screen, settings.CYAN, wall_camera, 1)

        if self._night:
            self.render_fog(player, camera)

        # draw hud on top of everything
        self._hud.draw(player)

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
        x, y = pos
        return self._hud.rect.collidepoint(x, y)

    def selected_item(self) -> int:
        return self._hud.selected_item

    def selected_mod(self) -> int:
        return self._hud.selected_mod

    def set_selected_item(self, idx: int) -> None:
        self._hud.selected_item = idx

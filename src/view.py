from typing import List, Tuple
import pygame as pg
from pygame.math import Vector2
from pygame.rect import Rect
from pygame.sprite import Sprite

import draw_utils
import images
import model
import mods
import settings
from creatures.players import Player
from hud import HUD
from settings import WIDTH, HEIGHT
from tilemap import TiledMap

NO_SELECTION = -1


class Camera:
    def __init__(self, width: int, height: int) -> None:
        self.rect = pg.Rect(0, 0, width, height)

    def get_shifted_rect(self, sprite: pg.sprite.Sprite) -> pg.Rect:
        return self.shift_by_topleft(sprite.rect)

    def shift_by_topleft(self, rect: pg.Rect) -> pg.Rect:
        return rect.move(self.rect.topleft)

    def update(self, target: pg.sprite.Sprite) -> None:
        x = -target.rect.centerx + int(WIDTH / 2)
        y = -target.rect.centery + int(HEIGHT / 2)

        # limit scrolling to map size
        x = min(0, x)  # left
        y = min(0, y)  # top
        x = max(-(self.rect.width - WIDTH), x)  # right
        y = max(-(self.rect.height - HEIGHT), y)  # bottom
        self.rect = pg.Rect(x, y, self.rect.width, self.rect.height)


class DungeonView(model.GroupsAccess):
    def __init__(self, screen: pg.Surface) -> None:

        self._screen = screen
        dim_screen = pg.Surface(screen.get_size()).convert_alpha()
        dim_screen.fill((0, 0, 0, 180))

        self.camera: Camera = Camera(800, 600)

        self._hud = HUD(self._screen)

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

        self._screen.blit(tile_map.img, self.camera.get_shifted_rect(tile_map))

        for sprite in self.groups.all_sprites:
            self._draw_sprite(sprite)

        if self._draw_debug:
            self._draw_debug_rects()

        if self._night:
            self.render_fog(player)

        if self.draw_teleport_text:
            self._draw_teleport_text()

        # draw hud on top of everything
        self._hud.draw(player)

    def _draw_sprite(self, sprite: Sprite) -> None:
        image = sprite.image
        rect = image.get_rect().copy()
        new_center = Vector2(sprite.pos)
        new_center.x += self.camera.rect.topleft[0]
        new_center.y += self.camera.rect.topleft[1]
        rect.center = new_center

        if self._rect_on_screen(rect):
            self._screen.blit(image, rect)

    def _draw_teleport_text(self) -> None:

        font = images.get_font(images.ZOMBIE_FONT)
        draw_utils.draw_text(self._screen, 'Press T to continue', font,
                             16, settings.GREEN, 16, 8)

    def _rect_on_screen(self, rect: Rect) -> bool:
        return self._screen.get_rect().colliderect(rect)

    def _draw_debug_rects(self) -> None:
        for sprite in self.groups.all_sprites:
            if hasattr(sprite, 'motion'):
                rect = sprite.motion.hit_rect
            else:
                rect = sprite.rect
            shifted_rect = self.camera.shift_by_topleft(rect)
            if self._rect_on_screen(shifted_rect):
                pg.draw.rect(self._screen, settings.CYAN, shifted_rect, 1)
        for obstacle in self.groups.walls:
            assert obstacle not in self.groups.all_sprites
            shifted_rect = self.camera.shift_by_topleft(obstacle.rect)
            if self._rect_on_screen(shifted_rect):
                pg.draw.rect(self._screen, settings.CYAN, shifted_rect, 1)

    def render_fog(self, player: Player) -> None:
        # draw the light mask (gradient) onto fog image
        self._fog.fill(settings.NIGHT_COLOR)
        self._light_rect.center = self.camera.get_shifted_rect(player).center
        self._fog.blit(self._light_mask, self._light_rect)
        self._screen.blit(self._fog, (0, 0), special_flags=pg.BLEND_MULT)

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


def _break_string_into_lines(max_chars_per_line: int,
                             string: str) -> List[str]:
    all_words = string.split(' ')
    lines = []
    current_line_length = 0
    current_line = ''
    for word in all_words:
        if len(word) + current_line_length + 1 > max_chars_per_line:
            lines.append(current_line)
            current_line = ''
            current_line_length = 0

        current_line += word + ' '
        current_line_length += len(word) + 1
    lines.append(current_line)

    return lines


class DecisionView(object):
    """Draws text for decision and transition scenes."""

    def __init__(self, screen: pg.Surface, prompt: str,
                 options: List[str], enumerate_options: bool = True) -> None:
        self._screen = screen

        max_chars_per_line = 70

        prompt_lines = _break_string_into_lines(max_chars_per_line, prompt)

        if enumerate_options:
            style = '{} - {}'
            options = [style.format(k + 1, opt) for k, opt in
                       enumerate(options)]
        self._text_lines = prompt_lines + [''] * 2 + options

    def draw(self) -> None:
        self._screen.fill(settings.BLACK)

        title_font = images.get_font(images.IMPACTED_FONT)

        num_lines = len(self._text_lines) + 1
        for idx, text in enumerate(self._text_lines, 0):
            draw_utils.draw_text(self._screen, text, title_font,
                                 24, settings.WHITE, settings.WIDTH / 2,
                                 settings.HEIGHT * (idx + 1) / num_lines,
                                 align="center")
        pg.display.flip()

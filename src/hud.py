from typing import List, Dict
import settings
import pygame as pg
from humanoids import Player
import images
import mods
from draw_utils import draw_text

NO_SELECTION = -1


class HUD(object):
    def __init__(self, screen: pg.Surface) -> None:

        self._screen = screen

        # HUD size & location
        self._hud_width = 473
        self._hud_height = 110
        hud_x = (settings.WIDTH - self._hud_width) / 2.0
        hud_y = settings.HEIGHT - self._hud_height
        self._hud_pos = (hud_x, hud_y)
        self._hud_bar_offset = 0
        self._bar_length = 260
        self._bar_height = 20
        self.rect = pg.Rect(hud_x,
                            hud_y,
                            self._hud_width,
                            self._hud_height)

        # generate rects for mods/backpack
        self.mod_rects = self.generate_mod_rects()
        self.backpack_rects = self.generate_backpack_rects()

        self.selected_mod = NO_SELECTION
        self.selected_item = NO_SELECTION

    def generate_mod_rects(self) -> Dict[mods.ModLocation, pg.Rect]:
        mod_size = 62
        x, y = self._hud_pos
        rects: Dict[mods.ModLocation, pg.Rect] = {}

        i = 0
        for loc in mods.ModLocation:
            x_i = x + i * (mod_size + 3)
            fill_rect = pg.Rect(x_i + 3, y + 3, mod_size, mod_size)
            rects[loc] = fill_rect
            i += 1

        return rects

    def generate_backpack_rects(self) -> List[pg.Rect]:
        item_size = 50
        x, y = self._hud_pos
        x += self._bar_length + 3
        y += 4
        rects: List[pg.Rect] = []
        for i in range(4):
            for j in range(2):
                x_i = x + i * (item_size + 2)
                y_i = y + j * (item_size + 2)
                fill_rect = pg.Rect(x_i, y_i, item_size, item_size)
                rects.append(fill_rect)
        return rects

    def draw(self, player: Player) -> None:
        self.draw_hud_base()
        self.draw_bar(player, 'health')
        self.draw_bar(player, 'energy')
        self.draw_mods(player)
        self.draw_backpack(player)

    def draw_hud_base(self) -> None:
        x, y = self._hud_pos
        fill_rect = pg.Rect(x, y, self._hud_width, self._hud_height)
        pg.draw.rect(self._screen, settings.HUDGREY, fill_rect)

    def draw_bar(self, player: Player, bar_type: str) -> None:

        if 'health' in bar_type:
            frac_full = player.health / player.max_health
            col = settings.HUDGREEN1
            back_col = settings.HUDGREEN2
            y_offset = 2 * self._bar_height
        else:
            frac_full = player.health / player.max_health
            col = settings.HUDBLUE1
            back_col = settings.HUDBLUE2
            y_offset = self._bar_height

        x = self._hud_pos[0] + self._hud_bar_offset
        y = settings.HEIGHT - y_offset - 2

        frac_full = max(0.0, frac_full)
        fill = frac_full * self._bar_length

        back_rect = pg.Rect(x, y, fill, self._bar_height)
        fill_rect = pg.Rect(x, y, self._bar_length, self._bar_height)
        outline_rect = pg.Rect(x, y, self._bar_length, self._bar_height)

        pg.draw.rect(self._screen, back_col, fill_rect)
        pg.draw.rect(self._screen, col, back_rect)
        pg.draw.rect(self._screen, settings.HUDDARK, outline_rect, 2)

    def draw_mods(self, player: Player) -> None:

        for idx, loc in enumerate(self.mod_rects):
            r = self.mod_rects[loc]
            col = settings.HUDDARK
            if self.selected_mod == idx:
                col = settings.RED
            pg.draw.rect(self._screen, col, r, 2)

        for idx, loc in enumerate(player.active_mods):
            img = player.active_mods[loc].equipped_image

            img = pg.transform.scale(img, (50, 50))

            img_rect = img.get_rect()
            img_rect.center = self.mod_rects[loc].center
            self._screen.blit(img, img_rect)

            title_font = images.get_font(images.ZOMBIE_FONT)
            draw_text(self._screen, str(idx + 1), title_font,
                      20, settings.WHITE, img_rect.x, img_rect.y,
                      align="center")

    def draw_backpack(self, player: Player) -> None:
        for idx, rect in enumerate(self.backpack_rects):
            color = settings.HUDDARK
            if self.selected_item == idx:
                color = settings.RED
            pg.draw.rect(self._screen, color, rect, 2)

        for idx in player.backpack:
            item_mod = player.backpack[idx]
            rect = self.backpack_rects[idx]
            img = item_mod.backpack_image
            img_rect = img.get_rect()
            img_rect.center = rect.center

            self._screen.blit(img, img_rect)

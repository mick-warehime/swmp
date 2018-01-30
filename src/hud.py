from typing import List, Dict, Tuple

import pygame as pg

import images
import mods
import settings
from creatures.players import Player
from draw_utils import draw_text

NO_SELECTION = -1


class HUD(object):
    def __init__(self, screen: pg.Surface) -> None:

        self._screen = screen

        # HUD size & location
        self._hud_width = 283
        self._hud_height = 68
        hud_x = (settings.WIDTH - self._hud_width) / 2.0
        hud_y = settings.HEIGHT - self._hud_height
        self._hud_pos = (hud_x, hud_y)
        self._hud_bar_offset = 0
        self._bar_length = 20
        self._bar_height = 75
        self.rect = pg.Rect(hud_x,
                            hud_y,
                            self._hud_width,
                            self._hud_height)

        # generate rects for mods/backpack
        self.mod_rects = self._generate_mod_rects()
        self.backpack_rects = self._generate_backpack_rects()
        self.backpack_base = self._generate_backpack_base()

        self.selected_mod = NO_SELECTION
        self.selected_item = NO_SELECTION
        self._backpack_hidden = True

    def draw(self, player: Player) -> None:
        self._draw_hud_base()
        self._draw_bar(player, 'health')
        self._draw_bar(player, 'energy')
        self._draw_mods(player)
        self._draw_backpack(player)

    def toggle_hide_backpack(self) -> None:
        self.selected_mod = NO_SELECTION
        self.selected_item = NO_SELECTION
        self._backpack_hidden = not self._backpack_hidden

    def clicked_hud(self, pos: Tuple[int, int]) -> bool:
        x, y = pos
        in_hud = self.rect.collidepoint(x, y)
        if in_hud:
            return True

        in_backpack = self.backpack_base.collidepoint(x, y)
        backpack_hidden = self._backpack_hidden
        return in_backpack and not backpack_hidden

    def _draw_hud_base(self) -> None:

        # hud base
        pg.draw.rect(self._screen, settings.HUDGREY, self.rect)

    def _draw_backpack_base(self) -> None:

        pg.draw.rect(self._screen, settings.HUDGREY, self.backpack_base)

    def _draw_bar(self, player: Player, bar_type: str) -> None:

        if 'health' in bar_type:
            frac_full = player.status.health / player.status.max_health
            col = settings.HUDGREEN1
            back_col = settings.HUDGREEN2
            x_offset = 0
        else:
            frac_full = player.energy_source.fraction_remaining
            col = settings.HUDBLUE1
            back_col = settings.HUDBLUE2
            x_offset = self._hud_width

        x = self._hud_pos[0] + self._hud_bar_offset + x_offset
        y = settings.HEIGHT - self._bar_height

        frac_full = max(0.0, frac_full)
        fill = frac_full * self._bar_height

        # need to shift the top left of the rect
        y_off = y - fill + self._bar_height

        back_rect = pg.Rect(x, y_off, self._bar_length, fill)
        fill_rect = pg.Rect(x, y, self._bar_length, self._bar_height)
        outline_rect = pg.Rect(x, y, self._bar_length, self._bar_height)

        pg.draw.rect(self._screen, back_col, fill_rect)
        pg.draw.rect(self._screen, col, back_rect)
        pg.draw.rect(self._screen, settings.HUDDARK, outline_rect, 2)

    def _draw_mods(self, player: Player) -> None:

        for idx, loc in enumerate(self.mod_rects):
            r = self.mod_rects[loc]
            col = settings.HUDDARK
            if self.selected_mod == idx:
                col = settings.RED
            pg.draw.rect(self._screen, col, r, 2)

        for idx, loc in enumerate(player.inventory.active_mods):
            mod = player.inventory.active_mods[loc]
            img = mod.equipped_image

            img = pg.transform.scale(img, (50, 50))

            img = self._draw_cooldown(mod.ability.cooldown_fraction, img)

            img_rect = img.get_rect()
            img_rect.center = self.mod_rects[loc].center
            self._screen.blit(img, img_rect)

            title_font = images.get_font(images.ZOMBIE_FONT)
            draw_text(self._screen, str(idx + 1), title_font,
                      20, settings.WHITE, img_rect.x, img_rect.y,
                      align="center")

            if mod.stackable:
                self._draw_mod_ammo(img_rect, mod, title_font)

    def _draw_cooldown(self, cooldown_fraction: float,
                       image: pg.Surface) -> pg.Surface:
        if cooldown_fraction >= 1:  # No bar necessary
            return image
        image = image.copy()  # Original image should be unchanged.
        col = settings.RED
        rect = image.get_rect()
        image_height = rect.height
        image_width = rect.width
        width = image_width * (1 - cooldown_fraction)
        if width > 0:
            cooldown_bar = pg.Rect(0, image_height - 7, width, 7)
            pg.draw.rect(image, col, cooldown_bar)
        return image

    def _draw_mod_ammo(self, img_rect: pg.Surface, mod: mods.Mod,
                       title_font: str) -> None:
        assert hasattr(mod.ability, 'uses_left')
        num_uses = mod.ability.uses_left

        x_coord = img_rect.x + img_rect.width
        y_coord = img_rect.y + img_rect.height
        draw_text(self._screen, str(num_uses), title_font,
                  20, settings.RED, x_coord, y_coord,
                  align="center")

    def _draw_backpack(self, player: Player) -> None:
        if self._backpack_hidden:
            return

        self._draw_backpack_base()

        for idx, rect in enumerate(self.backpack_rects):
            color = settings.HUDDARK
            if self.selected_item == idx:
                color = settings.RED
            pg.draw.rect(self._screen, color, rect, 2)

        for idx, item_mod in enumerate(player.inventory.backpack):
            if not player.inventory.backpack.slot_occupied(idx):
                continue
            rect = self.backpack_rects[idx]
            img = item_mod.backpack_image
            img_rect = img.get_rect()
            img_rect.center = rect.center

            self._screen.blit(img, img_rect)

            if item_mod.stackable:
                self._draw_mod_ammo(img_rect, item_mod,
                                    images.get_font(images.ZOMBIE_FONT))

    def _generate_mod_rects(self) -> Dict[mods.ModLocation, pg.Rect]:
        mod_size = 62
        x, y = self._hud_pos
        rects: Dict[mods.ModLocation, pg.Rect] = {}
        x += self._bar_length
        i = 0
        for loc in mods.ModLocation:
            x_i = x + i * (mod_size + 3)
            fill_rect = pg.Rect(x_i + 3, y + 3, mod_size, mod_size)
            rects[loc] = fill_rect
            i += 1

        return rects

    def _generate_backpack_rects(self) -> List[pg.Rect]:
        item_size = 50
        x = settings.WIDTH - item_size - 4
        y = 100
        rects: List[pg.Rect] = []
        for j in range(8):
            x_i = x
            y_i = y + j * (item_size + 2)
            fill_rect = pg.Rect(x_i, y_i, item_size, item_size)
            rects.append(fill_rect)
        return rects

    def _generate_backpack_base(self) -> pg.Rect:
        # backpack base
        x_b_i = self.backpack_rects[0][0] - 2
        x_b_f = self.backpack_rects[0][0] - 2
        y_b_i = self.backpack_rects[0][1]
        y_b_f = self.backpack_rects[-1][1] - 45

        b_fill = pg.Rect(x_b_i, y_b_i, x_b_f, y_b_f)
        return b_fill

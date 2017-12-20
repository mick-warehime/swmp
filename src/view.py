from typing import List, Tuple, Dict
import settings
import pygame as pg
from humanoid import Mob, Player
from model import Groups
from tilemap import Camera, TiledMap
import images
import mod

NO_SELECTION = -1


def draw_text(screen: pg.Surface, text: str, font_name: str,
              size: int, color: tuple, x: int, y: int,
              align: str = "topleft") -> None:
    fnt = pg.font.Font(font_name, size)
    text_surface = fnt.render(text, True, color)
    text_rect = text_surface.get_rect(**{align: (x, y)})
    screen.blit(text_surface, text_rect)


class DungeonView(object):
    def __init__(self, screen: pg.Surface) -> None:

        self._screen = screen
        dim_screen = pg.Surface(screen.get_size()).convert_alpha()
        dim_screen.fill((0, 0, 0, 180))

        # HUD size & location
        self._hud_width = 473
        self._hud_height = 110
        hud_x = (settings.WIDTH - self._hud_width) / 2.0
        hud_y = settings.HEIGHT - self._hud_height
        self._hud_pos = (hud_x, hud_y)
        self._hud_bar_offset = 0
        self._bar_length = 260
        self._bar_height = 20
        self._hud_rect = pg.Rect(hud_x,
                                 hud_y,
                                 self._hud_width,
                                 self._hud_height)

        # generate rects for mods/backpack
        self.mod_rects = self.generate_mod_rects()
        self.backpack_rects = self.generate_backpack_rects()

        self._selected_mod = NO_SELECTION
        self._selected_item = NO_SELECTION

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

    def generate_mod_rects(self) -> Dict[mod.ModLocation, pg.Rect]:
        mod_size = 62
        x, y = self._hud_pos
        rects: Dict[mod.ModLocation, pg.Rect] = {}

        i = 0
        for loc in mod.ModLocation:
            if loc == mod.ModLocation.BACKPACK:
                continue
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

        # HUD functions
        self.draw_hud(player)

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

    def draw_hud(self, player: Player) -> None:
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
            frac_full = player.health / settings.PLAYER_HEALTH
            col = settings.HUDGREEN1
            back_col = settings.HUDGREEN2
            y_offset = 2 * self._bar_height
        else:
            frac_full = player.health / settings.PLAYER_HEALTH
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
            if self._selected_mod == idx:
                col = settings.RED
            pg.draw.rect(self._screen, col, r, 2)

        for idx, loc in enumerate(player.active_mods):
            mod = player.active_mods[loc]
            img = mod.image

            img = pg.transform.scale(img, (70, 70))

            r = self.mod_rects[loc]
            self._screen.blit(img, r)

            title_font = images.get_font(images.ZOMBIE_FONT)
            draw_text(self._screen, str(idx + 1), title_font,
                      20, settings.WHITE, r.x + 10, r.y + 10, align="center")

    def draw_backpack(self, player: Player) -> None:
        for idx, rect in enumerate(self.backpack_rects):
            color = settings.HUDDARK
            if self._selected_item == idx:
                color = settings.RED
            pg.draw.rect(self._screen, color, rect, 2)

        for idx, item_mod in enumerate(player.backpack):
            rect = self.backpack_rects[idx]

            img = pg.transform.scale(item_mod.image, (rect.w, rect.h))
            self._screen.blit(img, rect)

    def try_click_mod(self, pos: Tuple[int, int]) -> None:
        equipables = [loc for loc in mod.ModLocation if
                      loc != mod.ModLocation.BACKPACK]
        rects = [self.mod_rects[l] for l in equipables]
        index = self.clicked_rect_index(rects, pos)
        if index == self._selected_mod:
            self._selected_mod = NO_SELECTION
        else:
            self._selected_mod = index

    def try_click_item(self, pos: Tuple[int, int]) -> None:
        index = self.clicked_rect_index(self.backpack_rects, pos)
        if index == self._selected_item:
            self._selected_item = NO_SELECTION
        else:
            self._selected_item = index

    def clicked_rect_index(self, rects: List[pg.Rect],
                           pos: Tuple[int, int]) -> int:

        x, y = pos
        for idx, r in enumerate(rects):
            if r.collidepoint(x, y):
                return idx
        return NO_SELECTION

    def clicked_hud(self, pos: Tuple[int, int]) -> bool:
        x, y = pos
        return self._hud_rect.collidepoint(x, y)

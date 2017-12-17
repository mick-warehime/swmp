import settings
from pygame import Surface, Rect, draw, font, BLEND_MULT
from pygame.sprite import LayeredUpdates, Group
from humanoid import Mob, Player
from tilemap import Camera, TiledMap
import images


def draw_text(screen: Surface, text: str, font_name: str,
              size: int, color: tuple, x: int, y: int,
              align: str = "topleft") -> None:
    fnt = font.Font(font_name, size)
    text_surface = fnt.render(text, True, color)
    text_rect = text_surface.get_rect(**{align: (x, y)})
    screen.blit(text_surface, text_rect)


class DungeonView(object):
    def __init__(self, screen: Surface) -> None:

        self._screen = screen
        dim_screen = Surface(screen.get_size()).convert_alpha()
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

        self._draw_debug = False
        self._night = False

        self._fog = Surface((settings.WIDTH, settings.HEIGHT))
        self._fog.fill(settings.NIGHT_COLOR)

        # lighting effect for night mode
        self._light_mask = images.get_image(images.LIGHT_MASK)
        self._light_rect = self._light_mask.get_rect()

        self.all_sprites = LayeredUpdates()
        self.walls = Group()
        self.mobs = Group()
        self.bullets = Group()
        self.items = Group()

    def set_sprites(self, all_sprites: LayeredUpdates) -> None:
        self.all_sprites = all_sprites

    def set_walls(self, walls: Group) -> None:
        self.walls = walls

    def set_items(self, items: Group) -> None:
        self.items = items

    def set_mobs(self, mobs: Group) -> None:
        self.mobs = mobs

    def draw(self,
             player: Player,
             map: TiledMap,
             map_img: Surface,
             camera: Camera) -> None:

        self._screen.blit(map_img, camera.apply(map))

        for sprite in self.all_sprites:
            if isinstance(sprite, Mob):
                sprite.draw_health()
            self._screen.blit(sprite.image, camera.apply(sprite))
            if self._draw_debug and hasattr(sprite, 'hit_rect'):
                sprite_camera = camera.apply_rect(sprite.hit_rect)
                draw.rect(self._screen, settings.CYAN, sprite_camera, 1)
        if self._draw_debug:
            for wall in self.walls:
                wall_camera = camera.apply_rect(wall.rect)
                draw.rect(self._screen, settings.CYAN, wall_camera, 1)

        if self._night:
            self.render_fog(player, camera)

        # HUD functions
        self.draw_hud(player)

    def render_fog(self, player: Player, camera: Camera) -> None:
        # draw the light mask (gradient) onto fog image
        self._fog.fill(settings.NIGHT_COLOR)
        self._light_rect.center = camera.apply(player).center
        self._fog.blit(self._light_mask, self._light_rect)
        self._screen.blit(self._fog, (0, 0), special_flags=BLEND_MULT)

    def toggle_debug(self) -> None:
        self._draw_debug = not self._draw_debug

    def toggle_night(self) -> None:
        self._night = not self._night

    def draw_hud(self, player: Player) -> None:
        self.draw_hud_base()
        self.draw_bar(player, 'health')
        self.draw_bar(player, 'energy')
        self.draw_skills()
        self.draw_backpack()

    def draw_hud_base(self) -> None:
        x, y = self._hud_pos
        fill_rect = Rect(x, y, self._hud_width, self._hud_height)
        draw.rect(self._screen, settings.HUDGREY, fill_rect)

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

        back_rect = Rect(x, y, fill, self._bar_height)
        fill_rect = Rect(x, y, self._bar_length, self._bar_height)
        outline_rect = Rect(x, y, self._bar_length, self._bar_height)

        draw.rect(self._screen, back_col, fill_rect)
        draw.rect(self._screen, col, back_rect)
        draw.rect(self._screen, settings.HUDDARK, outline_rect, 2)

    def draw_skills(self) -> None:
        skill_size = 62
        x, y = self._hud_pos
        for i in range(4):
            x_i = x + i * (skill_size + 3)
            fill_rect = Rect(x_i + 3, y + 3, skill_size, skill_size)
            draw.rect(self._screen, settings.HUDDARK, fill_rect, 2)

    def draw_backpack(self) -> None:
        item_size = 50
        x, y = self._hud_pos
        x += self._bar_length + 3
        y += 4
        for i in range(4):
            for j in range(2):
                x_i = x + i * (item_size + 2)
                y_i = y + j * (item_size + 2)
                fill_rect = Rect(x_i, y_i, item_size, item_size)
                draw.rect(self._screen, settings.HUDDARK, fill_rect, 2)

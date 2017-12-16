import pygame as pg
import settings
from pygame import Surface
from pygame.sprite import LayeredUpdates, Group
from humanoid import Mob, Player
from tilemap import Camera, TiledMap
import images


# HUD functions
def draw_player_health(surf: Surface, x: int, y: int, pct: float) -> None:
    if pct < 0:
        pct = 0
    bar_length = 100
    bar_height = 20
    fill = pct * bar_length
    outline_rect = pg.Rect(x, y, bar_length, bar_height)
    fill_rect = pg.Rect(x, y, fill, bar_height)
    if pct > 0.6:
        col = settings.GREEN
    elif pct > 0.3:
        col = settings.YELLOW
    else:
        col = settings.RED
    pg.draw.rect(surf, col, fill_rect)
    pg.draw.rect(surf, settings.WHITE, outline_rect, 2)


def draw_text(screen: pg.Surface, text: str, font_name: str,
              size: int, color: tuple, x: int, y: int,
              align: str = "topleft") -> None:
    font = pg.font.Font(font_name, size)
    text_surface = font.render(text, True, color)
    text_rect = text_surface.get_rect(**{align: (x, y)})
    screen.blit(text_surface, text_rect)


class DungeonView(object):
    def __init__(self, screen: Surface) -> None:

        self._screen = screen
        dim_screen = Surface(screen.get_size()).convert_alpha()
        dim_screen.fill((0, 0, 0, 180))

        self._draw_debug = False
        self._night = False

        self._fog = pg.Surface((settings.WIDTH, settings.HEIGHT))
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
                pg.draw.rect(self._screen, settings.CYAN, sprite_camera, 1)
        if self._draw_debug:
            for wall in self.walls:
                wall_camera = camera.apply_rect(wall.rect)
                pg.draw.rect(self._screen, settings.CYAN, wall_camera, 1)

        if self._night:
            self.render_fog(player, camera)

        # HUD functions
        remaining_health = player.health / settings.PLAYER_HEALTH
        draw_player_health(self._screen, 10, 10, remaining_health)
        zombies_str = 'Zombies: {}'.format(len(self.mobs))
        hud_font = images.get_font(images.IMPACTED_FONT)
        draw_text(self._screen, zombies_str, hud_font, 30, settings.WHITE,
                  settings.WIDTH - 10, 10, align="topright")

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

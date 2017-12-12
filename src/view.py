import pygame as pg
import settings
from pygame import Surface
from pygame.sprite import LayeredUpdates, Group
from sprites import Mob, Player
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


class DungeonView(object):
    def __init__(self, screen: Surface) -> None:

        self.screen = screen
        self.dim_screen = Surface(screen.get_size()).convert_alpha()
        self.dim_screen.fill((0, 0, 0, 180))

        self.all_sprites = LayeredUpdates()
        self.walls = Group()
        self.mobs = Group()
        self.bullets = Group()
        self.items = Group()

        self.draw_debug = False
        self.night = False

        self.fog = pg.Surface((settings.WIDTH, settings.HEIGHT))
        self.fog.fill(settings.NIGHT_COLOR)

        # lighting effect
        self.light_mask = images.get_image(images.LIGHT_MASK)
        self.light_rect = self.light_mask.get_rect()

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
             camera: Camera,
             paused: bool) -> None:

        self.screen.blit(map_img, camera.apply(map))

        for sprite in self.all_sprites:
            if isinstance(sprite, Mob):
                sprite.draw_health()
            self.screen.blit(sprite.image, camera.apply(sprite))
            if self.draw_debug and hasattr(sprite, 'hit_rect'):
                sprite_camera = camera.apply_rect(sprite.hit_rect)
                pg.draw.rect(self.screen, settings.CYAN, sprite_camera, 1)
        if self.draw_debug:
            for wall in self.walls:
                wall_camera = camera.apply_rect(wall.rect)
                pg.draw.rect(self.screen, settings.CYAN, wall_camera, 1)

        if self.night:
            self.render_fog(player, camera)

        # HUD functions
        remaining_health = player.health / settings.PLAYER_HEALTH
        draw_player_health(self.screen, 10, 10, remaining_health)
        zombies_str = 'Zombies: {}'.format(len(self.mobs))
        hud_font = images.get_font(images.IMPACTED_FONT)
        self.draw_text(zombies_str, hud_font, 30, settings.WHITE,
                       settings.WIDTH - 10, 10, align="topright")
        if paused:
            title_font = images.get_font(images.ZOMBIE_FONT)
            self.screen.blit(self.dim_screen, (0, 0))
            self.draw_text("Paused", title_font, 105,
                           settings.RED, settings.WIDTH / 2,
                           settings.HEIGHT / 2, align="center")

    def draw_text(self, text: str, font_name: str, size: int, color: tuple,
                  x: int, y: int, align: str = "topleft") -> None:
        font = pg.font.Font(font_name, size)
        text_surface = font.render(text, True, color)
        text_rect = text_surface.get_rect(**{align: (x, y)})
        self.screen.blit(text_surface, text_rect)

    def render_fog(self, player: Player, camera: Camera) -> None:
        # draw the light mask (gradient) onto fog image
        self.fog.fill(settings.NIGHT_COLOR)
        self.light_rect.center = camera.apply(player).center
        self.fog.blit(self.light_mask, self.light_rect)
        self.screen.blit(self.fog, (0, 0), special_flags=pg.BLEND_MULT)

    def game_over(self) -> None:
        self.screen.fill(settings.BLACK)
        title_font = images.get_font(images.ZOMBIE_FONT)
        self.draw_text("GAME OVER", title_font, 100, settings.RED,
                       settings.WIDTH / 2, settings.HEIGHT / 2,
                       align="center")
        self.draw_text("Press a key to start", title_font, 75,
                       settings.WHITE, settings.WIDTH / 2,
                       settings.HEIGHT * 3 / 4, align="center")

    def toggle_debug(self) -> None:
        self.draw_debug = not self.draw_debug

    def toggle_night(self) -> None:
        self.night = not self.night

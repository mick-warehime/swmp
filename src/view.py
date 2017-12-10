import os
import pygame as pg
import settings
from pygame import Surface
from pygame.sprite import LayeredUpdates, Group
from sprites import Mob, Player
from tilemap import Camera, TiledMap


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

        # lighting effect
        img_folder = 'img'
        self.fog = pg.Surface((settings.WIDTH, settings.HEIGHT))
        self.fog.fill(settings.NIGHT_COLOR)
        light_img_path = os.path.join(img_folder, settings.LIGHT_MASK)

        light_mask = pg.image.load(light_img_path).convert_alpha()
        self.light_mask = light_mask
        self.light_mask = pg.transform.scale(light_mask, settings.LIGHT_RADIUS)
        self.light_rect = self.light_mask.get_rect()

    def set_sprites(self, all_sprites: LayeredUpdates) -> None:
        self.all_sprites = all_sprites

    def draw(self,
             player: Player,
             map: TiledMap,
             map_img: Surface,
             camera: Camera) -> None:

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

    def render_fog(self, player: Player, camera: Camera) -> None:
        # draw the light mask (gradient) onto fog image
        self.fog.fill(settings.NIGHT_COLOR)
        self.light_rect.center = camera.apply(player).center
        self.fog.blit(self.light_mask, self.light_rect)
        self.screen.blit(self.fog, (0, 0), special_flags=pg.BLEND_MULT)

    def toggle_debug(self) -> None:
        self.draw_debug = not self.draw_debug

    def toggle_night(self) -> None:
        self.night = not self.night

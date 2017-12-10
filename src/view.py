import pygame as pg
import settings
from pygame import Surface
from pygame.sprite import LayeredUpdates, Group
from sprites import Mob
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
        self.paused = False
        self.night = False

    def set_sprites(self, all_sprites: LayeredUpdates) -> None:
        self.all_sprites = all_sprites

    def draw(self,
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

    def toggle_debug(self) -> None:
        self.draw_debug = not self.draw_debug

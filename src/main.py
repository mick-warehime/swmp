# Tilemap Demo
# KidsCanCode 2017
from typing import Dict, List

import pygame as pg
from pygame.sprite import LayeredUpdates, Group, spritecollide, groupcollide
from pygame.math import Vector2
import sys
from random import choice, random
from os import path
import settings
from sprites import Player, Mob, Obstacle, Item, collide_hit_rect
import tilemap
import controller as ctrl


# HUD functions
def draw_player_health(surf: pg.Surface, x: int, y: int, pct: float) -> None:
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


class Game:
    def __init__(self) -> None:
        self.zombie_hit_sounds: List[pg.mixer.Sound] = []
        self.player_hit_sounds: List[pg.mixer.Sound] = []
        self.zombie_moan_sounds: List[pg.mixer.Sound] = []
        self.weapon_sounds: Dict[str, List[pg.mixer.Sound]] = {}
        self.effects_sounds: Dict[str, pg.mixer.Sound] = {}
        self.item_images: Dict[str, pg.Surface] = {}
        self.gun_flashes: List[pg.Surface] = []
        self.bullet_images: Dict[str, pg.Surface] = {}
        self.map_folder: str = ''
        self.title_font: str = ''
        self.hud_font: str = ''

        pg.mixer.pre_init(44100, -16, 4, 2048)
        pg.init()
        self.screen = pg.display.set_mode((settings.WIDTH, settings.HEIGHT))
        pg.display.set_caption(settings.TITLE)
        self.clock = pg.time.Clock()
        self.load_data()
        self.dim_screen = pg.Surface(self.screen.get_size()).convert_alpha()
        self.dim_screen.fill((0, 0, 0, 180))

        self.all_sprites = LayeredUpdates()
        self._init_groups()

        self.controller: ctrl.Controller = ctrl.Controller()
        self.controller.set_binding(pg.K_ESCAPE, self.quit)
        self.controller.set_binding(pg.K_n, self.toggle_night)
        self.controller.set_binding(pg.K_h, self.toggle_debug)
        self.controller.set_binding(pg.K_p, self.toggle_paused)

    def draw_text(self, text: str, font_name: str, size: int, color: tuple,
                  x: int, y: int, align: str = "topleft") -> None:
        font = pg.font.Font(font_name, size)
        text_surface = font.render(text, True, color)
        text_rect = text_surface.get_rect(**{align: (x, y)})
        self.screen.blit(text_surface, text_rect)

    def load_data(self) -> None:
        game_folder = path.dirname(__file__)
        img_folder = path.join(game_folder, 'img')
        snd_folder = path.join(game_folder, 'snd')
        music_folder = path.join(game_folder, 'music')

        self.map_folder = path.join(game_folder, 'maps')

        self.title_font = path.join(img_folder, 'ZOMBIE.TTF')
        self.hud_font = path.join(img_folder, 'Impacted2.0.ttf')

        plyr_img_path = path.join(img_folder, settings.PLAYER_IMG)
        self.player_img = pg.image.load(plyr_img_path).convert_alpha()
        blt_img_path = path.join(img_folder, settings.BULLET_IMG)
        blt_img = pg.image.load(blt_img_path).convert_alpha()
        self.bullet_images['lg'] = blt_img
        self.bullet_images['sm'] = pg.transform.scale(blt_img, (10, 10))

        mob_img_path = path.join(img_folder, settings.MOB_IMG)
        self.mob_img = pg.image.load(mob_img_path).convert_alpha()

        splat_img_path = path.join(img_folder, settings.SPLAT)
        self.splat = pg.image.load(splat_img_path).convert_alpha()
        self.splat = pg.transform.scale(self.splat, (64, 64))
        for img in settings.MUZZLE_FLASHES:
            img_path = path.join(img_folder, img)
            self.gun_flashes.append(pg.image.load(img_path).convert_alpha())
        for item in settings.ITEM_IMAGES:
            img_path = path.join(img_folder, settings.ITEM_IMAGES[item])
            self.item_images[item] = pg.image.load(img_path).convert_alpha()
        # lighting effect
        self.fog = pg.Surface((settings.WIDTH, settings.HEIGHT))
        self.fog.fill(settings.NIGHT_COLOR)
        light_img_path = path.join(img_folder, settings.LIGHT_MASK)

        light_mask = pg.image.load(light_img_path).convert_alpha()
        self.light_mask = light_mask
        self.light_mask = pg.transform.scale(light_mask, settings.LIGHT_RADIUS)
        self.light_rect = self.light_mask.get_rect()
        # Sound loading
        pg.mixer.music.load(path.join(music_folder, settings.BG_MUSIC))
        for label, file_name in settings.EFFECTS_SOUNDS.items():
            sound_path = path.join(snd_folder, file_name)
            self.effects_sounds[label] = pg.mixer.Sound(sound_path)
        for weapon in settings.WEAPON_SOUNDS:
            self.weapon_sounds[weapon] = []
            for sound_file in settings.WEAPON_SOUNDS[weapon]:
                s = pg.mixer.Sound(path.join(snd_folder, sound_file))
                s.set_volume(0.3)
                self.weapon_sounds[weapon].append(s)
        for sound_file in settings.ZOMBIE_MOAN_SOUNDS:
            s = pg.mixer.Sound(path.join(snd_folder, sound_file))
            s.set_volume(0.2)
            self.zombie_moan_sounds.append(s)
        for sound_file in settings.PLAYER_HIT_SOUNDS:
            snd_path = path.join(snd_folder, sound_file)
            self.player_hit_sounds.append(pg.mixer.Sound(snd_path))
        for sound_file in settings.ZOMBIE_HIT_SOUNDS:
            snd_path = path.join(snd_folder, sound_file)
            self.zombie_hit_sounds.append(pg.mixer.Sound(snd_path))

    def new(self) -> None:
        # initialize all variables and do all the setup for a new game
        self.all_sprites = LayeredUpdates()
        self._init_groups()
        self.map = tilemap.TiledMap(path.join(self.map_folder, 'level1.tmx'))
        self.map_img = self.map.make_map()
        self.map.rect = self.map_img.get_rect()
        for tile_object in self.map.tmxdata.objects:
            obj_center = Vector2(tile_object.x + tile_object.width / 2,
                                 tile_object.y + tile_object.height / 2)
            if tile_object.name == 'player':
                self.player = Player(self, obj_center.x, obj_center.y)
            if tile_object.name == 'zombie':
                Mob(self, obj_center.x, obj_center.y)
            if tile_object.name == 'wall':
                Obstacle(self, tile_object.x, tile_object.y,
                         tile_object.width, tile_object.height)
            if tile_object.name in ['health', 'shotgun']:
                Item(self, obj_center, tile_object.name)
        self.camera = tilemap.Camera(self.map.width, self.map.height)
        self.draw_debug = False
        self.paused = False
        self.night = False
        self.effects_sounds['level_start'].play()

    def _init_groups(self) -> None:
        self.walls = Group()
        self.mobs = Group()
        self.bullets = Group()
        self.items = Group()

    def run(self) -> None:
        # game loop - set self.playing = False to end the game
        self.playing = True
        pg.mixer.music.play(loops=-1)
        while self.playing:
            # fix for Python 2.x
            self.dt = self.clock.tick(settings.FPS) / 1000.0
            self.events()
            if not self.paused:
                self.update()
            self.draw()

    @staticmethod
    def quit() -> None:
        pg.quit()
        sys.exit()

    def update(self) -> None:
        # update portion of the game loop
        self.all_sprites.update()
        self.camera.update(self.player)
        # game over?
        if len(self.mobs) == 0:
            self.playing = False
        # player hits items
        hits = spritecollide(self.player, self.items, False)
        for hit in hits:
            full_health = self.player.health >= settings.PLAYER_HEALTH
            if hit.type == 'health' and not full_health:
                hit.kill()
                self.effects_sounds['health_up'].play()
                self.player.add_health(settings.HEALTH_PACK_AMOUNT)
            if hit.type == 'shotgun':
                hit.kill()
                self.effects_sounds['gun_pickup'].play()
                self.player.weapon = 'shotgun'
        # mobs hit player
        hits = spritecollide(self.player, self.mobs, False, collide_hit_rect)
        for hit in hits:
            if random() < 0.7:
                choice(self.player_hit_sounds).play()
            self.player.health -= settings.MOB_DAMAGE
            hit.vel = Vector2(0, 0)
            if self.player.health <= 0:
                self.playing = False
        if hits:
            self.player.hit()
            knock_back = Vector2(settings.MOB_KNOCKBACK, 0)
            self.player.pos += knock_back.rotate(-hits[0].rot)
        # bullets hit mobs
        hits = groupcollide(self.mobs, self.bullets, False, True)
        for mob in hits:
            for bullet in hits[mob]:
                mob.health -= bullet.damage
            mob.vel = Vector2(0, 0)

    def draw_grid(self) -> None:
        for x in range(0, settings.WIDTH, settings.TILESIZE):
            box_max_x = (x, settings.HEIGHT)
            pg.draw.line(self.screen, settings.LIGHTGREY, (x, 0), box_max_x)
        for y in range(0, settings.HEIGHT, settings.TILESIZE):
            box_max_y = (settings.WIDTH, y)
            pg.draw.line(self.screen, settings.LIGHTGREY, (0, y), box_max_y)

    def render_fog(self) -> None:
        # draw the light mask (gradient) onto fog image
        self.fog.fill(settings.NIGHT_COLOR)
        self.light_rect.center = self.camera.apply(self.player).center
        self.fog.blit(self.light_mask, self.light_rect)
        self.screen.blit(self.fog, (0, 0), special_flags=pg.BLEND_MULT)

    def draw(self) -> None:
        pg.display.set_caption("{:.2f}".format(self.clock.get_fps()))
        # self.screen.fill(BGCOLOR)
        self.screen.blit(self.map_img, self.camera.apply(self.map))
        # self.draw_grid()
        for sprite in self.all_sprites:
            if isinstance(sprite, Mob):
                sprite.draw_health()
            self.screen.blit(sprite.image, self.camera.apply(sprite))
            if self.draw_debug:
                camera = self.camera.apply_rect(sprite.hit_rect)
                pg.draw.rect(self.screen, settings.CYAN, camera, 1)
        if self.draw_debug:
            for wall in self.walls:
                camera = self.camera.apply_rect(wall.rect)
                pg.draw.rect(self.screen, settings.CYAN, camera, 1)

        if self.night:
            self.render_fog()
        # HUD functions
        remaining_health = self.player.health / settings.PLAYER_HEALTH
        draw_player_health(self.screen, 10, 10, remaining_health)
        zombies_str = 'Zombies: {}'.format(len(self.mobs))
        self.draw_text(zombies_str, self.hud_font, 30, settings.WHITE,
                       settings.WIDTH - 10, 10, align="topright")
        if self.paused:
            self.screen.blit(self.dim_screen, (0, 0))
            self.draw_text("Paused", self.title_font, 105,
                           settings.RED, settings.WIDTH / 2,
                           settings.HEIGHT / 2, align="center")
        pg.display.flip()

    def events(self) -> None:
        # catch all events here
        for event in pg.event.get():
            if event.type == pg.QUIT:
                self.quit()
            if event.type == pg.KEYDOWN:
                # check for any keys/clicks
                self.controller.update()

    def toggle_night(self) -> None:
        self.night = not self.night

    def toggle_debug(self) -> None:
        self.draw_debug = not self.draw_debug

    def toggle_paused(self) -> None:
        self.paused = not self.paused

    def show_go_screen(self) -> None:
        self.screen.fill(settings.BLACK)
        self.draw_text("GAME OVER", self.title_font, 100, settings.RED,
                       settings.WIDTH / 2, settings.HEIGHT / 2,
                       align="center")
        self.draw_text("Press a key to start", self.title_font, 75,
                       settings.WHITE, settings.WIDTH / 2,
                       settings.HEIGHT * 3 / 4, align="center")
        pg.display.flip()
        self.wait_for_key()

    def wait_for_key(self) -> None:
        pg.event.wait()
        waiting = True
        while waiting:
            self.clock.tick(settings.FPS)
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    waiting = False
                    self.quit()
                if event.type == pg.KEYUP:
                    waiting = False


# create the game object
g = Game()
while True:
    g.new()
    g.run()
    g.show_go_screen()

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
import view


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

        pg.mixer.pre_init(44100, -16, 4, 2048)
        pg.init()
        self.screen = pg.display.set_mode((settings.WIDTH, settings.HEIGHT))
        self.clock = pg.time.Clock()
        self.load_data()
        self.dim_screen = pg.Surface(self.screen.get_size()).convert_alpha()
        self.dim_screen.fill((0, 0, 0, 180))

        self.all_sprites = LayeredUpdates()
        self._init_groups()

        self.controller: ctrl.Controller = ctrl.Controller()
        self.view: view.DungeonView = view.DungeonView(self.screen)

    def load_data(self) -> None:
        game_folder = path.dirname(__file__)
        img_folder = path.join(game_folder, 'img')
        snd_folder = path.join(game_folder, 'snd')
        music_folder = path.join(game_folder, 'music')

        self.map_folder = path.join(game_folder, 'maps')

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
        self.paused = False
        self.effects_sounds['level_start'].play()

        # Temporary - eventually this should be one call to construct
        # a DungeonController that takes only a map and generates all the
        # sprites from that map
        self.view = view.DungeonView(self.screen)
        self.view.set_sprites(self.all_sprites)
        self.view.set_walls(self.walls)
        self.view.set_items(self.items)
        self.view.set_mobs(self.mobs)
        self.set_default_controls()

    def set_default_controls(self) -> None:

        self.controller.bind(pg.K_ESCAPE, self.quit)
        self.controller.bind_down(pg.K_n, self.view.toggle_night)
        self.controller.bind_down(pg.K_h, self.view.toggle_debug)
        self.controller.bind_down(pg.K_p, self.toggle_paused)

        # players controls
        counterclockwise = self.player.turn_counterclockwise
        clockwise = self.player.turn_clockwise
        self.controller.bind(pg.K_q, counterclockwise)
        self.controller.bind(pg.K_e, clockwise)

        self.controller.bind(pg.K_LEFT, self.player.move_left)
        self.controller.bind(pg.K_a, self.player.move_left)

        self.controller.bind(pg.K_RIGHT, self.player.move_right)
        self.controller.bind(pg.K_d, self.player.move_right)

        self.controller.bind(pg.K_UP, self.player.move_up)
        self.controller.bind(pg.K_w, self.player.move_up)

        self.controller.bind(pg.K_DOWN, self.player.move_down)
        self.controller.bind(pg.K_s, self.player.move_down)

        self.controller.bind(pg.K_SPACE, self.player.shoot)

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
            self.update()
            self.draw()

    @staticmethod
    def quit() -> None:
        pg.quit()
        sys.exit()

    def update(self) -> None:
        # always update the controller
        self.controller.update()
        if self.paused:
            return

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

    def draw(self) -> None:

        pg.display.set_caption("{:.2f}".format(self.clock.get_fps()))

        self.view.draw(self.player,
                       self.map,
                       self.map_img,
                       self.camera,
                       self.paused)

        pg.display.flip()

    def events(self) -> None:
        # catch all events here
        for event in pg.event.get():
            if event.type == pg.QUIT:
                self.quit()

    def toggle_paused(self) -> None:
        self.paused = not self.paused

    def show_go_screen(self) -> None:
        self.view.game_over()
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

import pygame as pg
from pygame.sprite import LayeredUpdates, Group, spritecollide, groupcollide
from pygame.math import Vector2
import sys
from random import random
from os import path
import settings
from sprites import Player, Mob, Obstacle, Item, collide_hit_rect
import tilemap
import controller as ctrl
import view
import sounds
import images


class Game(object):
    def __init__(self) -> None:

        pg.mixer.pre_init(44100, -16, 4, 2048)

        pg.init()

        self.screen = pg.display.set_mode((settings.WIDTH, settings.HEIGHT))
        self.clock = pg.time.Clock()

        self.dim_screen = pg.Surface(self.screen.get_size()).convert_alpha()
        self.dim_screen.fill((0, 0, 0, 180))

        # needs to happen after the video mode has been set
        images.initialize_images()

        # needs to happen after a valid mixer is available
        sounds.initialize_sounds()

        self.all_sprites = LayeredUpdates()
        self._init_groups()

        self.controller: ctrl.Controller = ctrl.Controller()
        self.view: view.DungeonView = view.DungeonView(self.screen)

    def new(self) -> None:
        # initialize all variables and do all the setup for a new game
        self.all_sprites = LayeredUpdates()
        self._init_groups()

        game_folder = path.dirname(__file__)
        map_folder = path.join(game_folder, 'maps')
        self.map = tilemap.TiledMap(path.join(map_folder, 'level1.tmx'))
        self.map_img = self.map.make_map()
        self.map.rect = self.map_img.get_rect()
        for tile_object in self.map.tmxdata.objects:
            obj_center = Vector2(tile_object.x + tile_object.width / 2,
                                 tile_object.y + tile_object.height / 2)
            if tile_object.name == 'player':
                pos = Vector2(obj_center.x, obj_center.y)
                self.player = Player(self, pos)
            if tile_object.name == 'zombie':
                pos = Vector2(obj_center.x, obj_center.y)
                Mob(self, pos)
            if tile_object.name == 'wall':
                pos = Vector2(tile_object.x, tile_object.y)
                Obstacle(self, pos, tile_object.width, tile_object.height)
            if tile_object.name in ['health', 'shotgun']:
                Item(self, obj_center, tile_object.name)
        self.camera = tilemap.Camera(self.map.width, self.map.height)
        self.paused = False
        sounds.play(sounds.LEVEL_START)

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
        self.controller.bind_mouse(ctrl.MOUSE_LEFT, self.player.shoot)

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
                sounds.play(sounds.HEALTH_UP)
                self.player.add_health(settings.HEALTH_PACK_AMOUNT)
            if hit.type == 'shotgun':
                hit.kill()
                sounds.play(sounds.GUN_PICKUP)
                self.player.set_weapon('shotgun')
        # mobs hit player
        hits = spritecollide(self.player, self.mobs, False, collide_hit_rect)
        for hit in hits:
            if random() < 0.7:
                sounds.player_hit_sound()
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

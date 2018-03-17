import sys

import pygame as pg

import controllers
import controllers.base
import images
import model
import settings
import sounds
from data.input_output import load_quest_data
from draw_utils import draw_text
from quests.quest import Quest


class Game(object):
    def __init__(self) -> None:

        pg.mixer.pre_init(44100, -16, 4, 2048)

        pg.init()

        self._screen = pg.display.set_mode(
            (settings.WIDTH, settings.HEIGHT))

        self._dim_screen = pg.Surface(
            self._screen.get_size()).convert_alpha()
        self._dim_screen.fill((0, 0, 0, 180))

        # needs to happen before we make any controllers
        controllers.base.initialize_controller(self._screen, self._quit)

        # needs to happen after the video mode has been set
        images.initialize_images()

        # needs to happen after a valid mixer is available
        sounds.initialize_sounds()

        self._clock = pg.time.Clock()

        timer = model.Timer(self._clock)
        groups = model.Groups()
        model.initialize(groups, timer)

        self._paused = False

    def new(self) -> None:

        self.quest_graph = Quest(load_quest_data('zombie_quest'))

        sounds.play(sounds.LEVEL_START)

    def run(self) -> None:
        # game loop - set self.playing = False to end the game
        pg.mixer.music.play(loops=-1)
        while True:

            self._handle_events()

            # needs to be called every frame to throttle max framerate
            self._clock.tick(settings.FPS)
            pg.display.set_caption("{:.2f}".format(self._clock.get_fps()))

            self.quest_graph.update_and_draw()

            if self._paused:
                self._pause_game()

    def show_go_screen(self) -> None:
        self._game_over()
        self._wait_for_key()

    def _quit(self) -> None:
        pg.quit()
        sys.exit()

    def _handle_events(self) -> None:
        # catch all events here
        for event in pg.event.get():
            if event.type == pg.QUIT:
                self._quit()

    def _toggle_paused(self) -> None:
        self._paused = not self._paused

    def _wait_for_key(self) -> None:
        pg.event.wait()
        waiting = True
        while waiting:
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    waiting = False
                    self._quit()
                if event.type == pg.KEYDOWN:
                    waiting = False

    def _game_over(self) -> None:
        self._screen.fill(settings.BLACK)
        title_font = images.get_font(images.ZOMBIE_FONT)
        draw_text(self._screen, "GAME OVER", title_font,
                  100, settings.RED, settings.WIDTH / 2,
                  settings.HEIGHT / 2, align="center")
        draw_text(self._screen, "Press a key to start", title_font,
                  75, settings.WHITE, settings.WIDTH / 2,
                  settings.HEIGHT * 3 / 4, align="center")
        pg.display.flip()

    def _pause_game(self) -> None:
        title_font = images.get_font(images.ZOMBIE_FONT)
        self._screen.blit(self._dim_screen, (0, 0))
        draw_text(self._screen, "Paused", title_font, 105,
                  settings.RED, settings.WIDTH / 2,
                  settings.HEIGHT / 2, align="center")

        pg.display.flip()
        self._wait_for_key()
        self._paused = False


g = Game()
while True:
    g.new()
    g.run()
    g.show_go_screen()

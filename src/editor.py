"""Editor for creating new quests."""
import sys

import pygame as pg

import controllers
import controllers.base

import settings
from controllers.menu_controller import MenuController
from view import images, sounds
from view.draw_utils import draw_text
from view.screen import ScreenAccess

ScreenAccess.initialize()


class Editor(ScreenAccess):
    def __init__(self) -> None:
        super().__init__()

        pg.mixer.pre_init(44100, -16, 4, 2048)

        pg.init()

        # needs to happen before we make any controllers
        controllers.base.initialize_controller(self._quit)

        # needs to happen after the video mode has been set
        images.initialize_images()

        # needs to happen after a valid mixer is available
        sounds.initialize_sounds()

        self._clock = pg.time.Clock()

        self._controller: MenuController = None

    def start(self) -> None:
        self._controller = MenuController()

        print('Initializing game')

    def run(self) -> None:

        while True:
            self._handle_events()

            # needs to be called every frame to throttle max framerate
            self._clock.tick(settings.FPS)
            pg.display.set_caption("{:.2f}".format(self._clock.get_fps()))

            self._controller.update()

    # def show_go_screen(self) -> None:
    #     self._wait_for_key()

    def _quit(self) -> None:
        pg.quit()
        sys.exit()

    def _handle_events(self) -> None:
        # catch all events here
        for event in pg.event.get():
            if event.type == pg.QUIT:
                self._quit()

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


app = Editor()
while True:
    app.start()
    app.run()
    # app.show_go_screen()

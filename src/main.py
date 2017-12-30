import pygame as pg
import sys
import settings
import sounds
import images
import controller
from draw_utils import draw_text
import quest


class Game(object):
    def __init__(self) -> None:

        pg.mixer.pre_init(44100, -16, 4, 2048)

        pg.init()

        self.screen = pg.display.set_mode((settings.WIDTH, settings.HEIGHT))

        self.dim_screen = pg.Surface(self.screen.get_size()).convert_alpha()
        self.dim_screen.fill((0, 0, 0, 180))

        # needs to happen before we make any controller
        controller.initialize_controller(self.screen, self.quit)

        # needs to happen after the video mode has been set
        images.initialize_images()

        # needs to happen after a valid mixer is available
        sounds.initialize_sounds()

        self.paused = False

    def new(self) -> None:

        self.quest = quest.Quest()
        self.next_dungeon()
        sounds.play(sounds.LEVEL_START)

    def next_dungeon(self) -> None:
        self.dungeon = self.quest.next_dungeon()
        if self.dungeon != quest.COMPLETE:
            self.dungeon.bind_down(pg.K_p, self.toggle_paused)

    def run(self) -> None:
        # game loop - set self.playing = False to end the game
        pg.mixer.music.play(loops=-1)
        while True:
            if self.dungeon == quest.COMPLETE:
                break

            self.events()
            self.update()

            if self.paused:
                self.pause_game()

            if self.dungeon.game_over():
                break

            if self.dungeon.dungeon_over():
                self.next_dungeon()

    def quit(self) -> None:
        pg.quit()
        sys.exit()

    def update(self) -> None:
        # always update the controller
        self.dungeon.update()
        self.dungeon.draw()

    def events(self) -> None:
        # catch all events here
        for event in pg.event.get():
            if event.type == pg.QUIT:
                self.quit()

    def toggle_paused(self) -> None:
        self.paused = not self.paused

    def show_go_screen(self) -> None:
        self.game_over()
        pg.display.flip()
        self.wait_for_key()

    def wait_for_key(self) -> None:
        pg.event.wait()
        waiting = True
        while waiting:
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    waiting = False
                    self.quit()
                if event.type == pg.KEYUP:
                    waiting = False

    def game_over(self) -> None:
        self.screen.fill(settings.BLACK)
        title_font = images.get_font(images.ZOMBIE_FONT)
        draw_text(self.screen, "GAME OVER", title_font,
                  100, settings.RED, settings.WIDTH / 2,
                  settings.HEIGHT / 2, align="center")
        draw_text(self.screen, "Press a key to start", title_font,
                  75, settings.WHITE, settings.WIDTH / 2,
                  settings.HEIGHT * 3 / 4, align="center")
        pg.display.flip()

    def pause_game(self) -> None:
        title_font = images.get_font(images.ZOMBIE_FONT)
        self.screen.blit(self.dim_screen, (0, 0))
        draw_text(self.screen, "Paused", title_font, 105,
                  settings.RED, settings.WIDTH / 2,
                  settings.HEIGHT / 2, align="center")

        pg.display.flip()

        while self.paused:
            pg.event.wait()
            self.dungeon.handle_input(only_handle=[pg.K_p])


g = Game()
while True:
    g.new()
    g.run()
    g.show_go_screen()

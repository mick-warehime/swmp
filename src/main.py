import pygame as pg
import sys
import settings
import sounds
import images
import controller
from draw_utils import draw_text
from dungeon_controller import DungeonController, Dungeon
from quests.resolutions import KillGroup, EnterZone


class Game(object):
    def __init__(self) -> None:

        pg.mixer.pre_init(44100, -16, 4, 2048)

        pg.init()

        self._screen = pg.display.set_mode((settings.WIDTH, settings.HEIGHT))

        self._dim_screen = pg.Surface(self._screen.get_size()).convert_alpha()
        self._dim_screen.fill((0, 0, 0, 180))

        # needs to happen before we make any controller
        controller.initialize_controller(self._screen, self._quit)

        # needs to happen after the video mode has been set
        images.initialize_images()

        # needs to happen after a valid mixer is available
        sounds.initialize_sounds()

        self._paused = False

    def new(self) -> None:

        dungeon = Dungeon('level1.tmx')
        res_data = dungeon.labeled_sprites

        resolutions = [KillGroup('quest'), KillGroup('player'),
                       EnterZone('exit', 'player')]

        for resolution in resolutions:
            resolution.load_data(res_data)

        self.scene_ctlr = DungeonController(dungeon, resolutions)
        # self.quest = quest.Quest()
        # self._next_scene()
        sounds.play(sounds.LEVEL_START)

    def run(self) -> None:
        # game loop - set self.playing = False to end the game
        pg.mixer.music.play(loops=-1)
        while True:
            # if self.quest.is_complete:
            #     break

            self._handle_events()
            self._update()

            if self._paused:
                self._pause_game()

            resolutions = self.scene_ctlr.resolved_resolutions()
            if resolutions:
                break

            if self.scene_ctlr.game_over():
                break

                # if self.scene_ctlr.should_exit():
                #     self._next_scene()

    def show_go_screen(self) -> None:
        self._game_over()
        self._wait_for_key()

    # def _next_scene(self) -> None:
    #     scene = self.quest.next_scene()
    #     if self.quest.is_complete:
    #         return
    #
    #     self.scene_ctlr = scene.get_controller()
    #     self.scene_ctlr.keyboard.bind_on_press(pg.K_p, self._toggle_paused)
    #
    #     if self._player is not None:
    #         self.scene_ctlr.set_player(self._player)
    #     else:
    #         self._player = self.scene_ctlr.player
    #
    #     scene.show_intro()

    def _quit(self) -> None:
        pg.quit()
        sys.exit()

    def _update(self) -> None:
        # always update the controller
        self.scene_ctlr.update()
        self.scene_ctlr.draw()

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

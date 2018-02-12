import sys
from typing import Union

import networkx
import pygame as pg

import controller
import images
import settings
import sounds
from creatures import players
from creatures.humanoids import Inventory, Status, HumanoidData
from draw_utils import draw_text
from quests.resolutions import Resolution
from quests.scenes import DecisionScene, DungeonScene, Scene


class Quest2(object):
    """Handles transitions between different Controllers (scenes)"""

    def __init__(self):

        self._player_data: HumanoidData = None
        self._graph = networkx.MultiDiGraph()

        root = DecisionScene('Lasers or rocks?', ['lasers please', 'rocks!'])
        self._graph.add_node(root)
        self._root_scene = root

        laser_scene = DungeonScene('level1.tmx')
        self._graph.add_node(laser_scene)
        self._graph.add_edge(root, laser_scene, key=0)

        rock_scene = DungeonScene('goto.tmx')
        self._graph.add_node(rock_scene)
        self._graph.add_edge(root, rock_scene, key=1)

        game_over_lose = DecisionScene('You lose!', ['play again'])
        self._graph.add_node(game_over_lose)
        self._graph.add_edge(game_over_lose, root, key=0)

        # DungeonScenes are currently constructed so the player death is the
        #  second resolution, and the win conditions are first and third.
        self._graph.add_edge(rock_scene, game_over_lose, key=1)
        self._graph.add_edge(laser_scene, game_over_lose, key=1)

        game_over_win = DecisionScene('You win!', ['play again'])
        self._graph.add_edge(game_over_win, root, key=0)
        self._graph.add_node(game_over_win)

        self._graph.add_edge(rock_scene, laser_scene, key=0)
        self._graph.add_edge(rock_scene, laser_scene, key=2)
        self._graph.add_edge(laser_scene, game_over_win, key=0)
        self._graph.add_edge(laser_scene, game_over_win, key=2)

        self._set_current_scene(root)

    def _set_current_scene(self, scene: Scene) -> None:
        self._current_scene = scene
        ctrl, resolutions = self._current_scene.make_controller_and_resolutions()
        self._current_ctrl = ctrl

        if self._current_scene is self._root_scene:
            self._player_data = HumanoidData(Status(players.PLAYER_HEALTH),
                                             Inventory())
        # TODO(dvirk): The initial DecisionScene has no Player, meaning that
        #  we cant use its inventory.
        if self._current_ctrl.player is not None:
            self._current_ctrl.set_player_data(self._player_data)

        # Output of out_edges is a list of tuples of the form
        # (source (Scene), sink(Scene), key (int))
        next_scenes = [(edge[2], edge[1]) for edge in
                       self._graph.out_edges(scene, keys=True)]
        next_scenes = sorted(next_scenes, key=lambda x: x[0])
        self._resolutions_to_scenes = {res: scene_tup[1] for res, scene_tup in
                                       zip(resolutions, next_scenes)}

    def update_and_draw(self):
        self._current_ctrl.update()
        self._current_ctrl.draw()

        resolution = self._resolved_resolution()
        if resolution is not None:
            next_scene = self._resolutions_to_scenes[resolution]
            self._set_current_scene(next_scene)

    def _resolved_resolution(self) -> Union[Resolution, None]:
        resolved = [res for res in self._resolutions_to_scenes if
                    res.is_resolved]

        if len(resolved) not in (0, 1):
            raise Warning('More than one resolved resolutions: {}. '
                          'Choosing first in list.'.format(resolved))

        if resolved:
            return resolved[0]
        else:
            return None

            # resolutions = self.current_node.resolved_resolutions()
            # if resolutions:
            #     resolution = resolutions[0]
            #     edges_out = self._graph.out_edges([self.current_node], data=True)
            #
            #     valid_edges = [edge for edge in edges_out if
            #                    edge[2]['resolution'] is resolution]
            #     assert len(valid_edges) == 1, 'Resolved resolution must ' \
            #                                   'correspond to exactly one edge.'
            #     self.current_node = valid_edges[0][1]


class Game(object):
    def __init__(self) -> None:

        pg.mixer.pre_init(44100, -16, 4, 2048)

        pg.init()

        self._screen = pg.display.set_mode(
            (settings.WIDTH, settings.HEIGHT))

        self._dim_screen = pg.Surface(
            self._screen.get_size()).convert_alpha()
        self._dim_screen.fill((0, 0, 0, 180))

        # needs to happen before we make any controller
        controller.initialize_controller(self._screen, self._quit)

        # needs to happen after the video mode has been set
        images.initialize_images()

        # needs to happen after a valid mixer is available
        sounds.initialize_sounds()

        self._paused = False

    def new(self) -> None:

        self.quest_graph = Quest2()

        sounds.play(sounds.LEVEL_START)

    def run(self) -> None:
        # game loop - set self.playing = False to end the game
        pg.mixer.music.play(loops=-1)
        while True:

            self._handle_events()

            self.quest_graph.update_and_draw()

            if self._paused:
                self._pause_game()

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

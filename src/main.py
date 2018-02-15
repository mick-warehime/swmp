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
from quests.scenes import Scene, make_scene


class Quest2(object):
    """Handles transitions between different Controllers (scenes)"""

    def __init__(self):

        self._player_data: HumanoidData = None
        self._graph = networkx.MultiDiGraph()

        lose_data = {'type': 'decision',
                     'prompt': 'You lose!',
                     'choices': [{'play again': 'root'}]}

        win_data = lose_data.copy()
        win_data['prompt'] = 'you win!'

        rock_resolutions = [{'kill group': {'group label': 'quest',
                                            'next scene': 'game over win'}},
                            {'condition': {'condition data': {'dead': None},
                                           'tested label': 'player',
                                           'next scene': 'game over lose'}},
                            {'enter zone': {'zone label': 'exit',
                                            'entering label': 'player',
                                            'next scene': 'game over win'}}]

        laser_resolutions = [{'kill group': {'group label': 'quest',
                                             'next scene': 'rock scene'}},
                             {'condition': {'condition data': {'dead': None},
                                            'tested label': 'player',
                                            'next scene': 'game over lose'}},
                             {'enter zone': {'zone label': 'exit',
                                             'entering label': 'player',
                                             'next scene': 'rock scene'}}]

        laser_scene_data = {'type': 'dungeon',
                            'map file': 'level1.tmx',
                            'resolutions': laser_resolutions}
        rock_scene_data = {'type': 'dungeon',
                           'map file': 'goto.tmx',
                           'resolutions': rock_resolutions}

        start_scene_data = {'type': 'decision',
                            'prompt': 'Lasers or rocks?',
                            'choices': [{'lasers please': 'laser scene'},
                                        {'rocks!': 'rock scene'}]}

        quest_data = {'root': start_scene_data,
                      'laser scene': laser_scene_data,
                      'rock scene': rock_scene_data,
                      'game over win': win_data,
                      'game over lose': lose_data}

        g2 = networkx.MultiDiGraph()
        for label, scene_data in quest_data.items():
            g2.add_node(make_scene(scene_data), label=label)

        scene_from_label = {info['label']: node
                            for node, info in g2.nodes.data()}

        for scene_label, scene in scene_from_label.items():
            scene_data = quest_data[scene_label]

            if scene_data['type'] == 'decision':
                for index, choice in enumerate(scene_data['choices']):
                    assert len(choice.values()) == 1
                    next_scene_label = list(choice.values())[0]
                    next_scene = scene_from_label[next_scene_label]
                    g2.add_edge(scene, next_scene, key=index)

            else:
                assert scene_data['type'] == 'dungeon'
                for index, resolution in enumerate(scene_data['resolutions']):
                    assert len(resolution.values()) == 1
                    res_data = list(resolution.values())[0]
                    next_scene_label = res_data['next scene']
                    next_scene = scene_from_label[next_scene_label]
                    g2.add_edge(scene, next_scene, key=index)

        root = scene_from_label['root']
        self._graph = g2
        self._root_scene = root
        self._set_current_scene(root)

        # root = make_scene(start_scene_data)
        # self._graph.add_node(root)
        # self._root_scene = root
        #
        # laser_scene = make_scene(laser_scene_data)
        # self._graph.add_node(laser_scene)
        # self._graph.add_edge(root, laser_scene, key=0)
        #
        # rock_scene = make_scene(rock_scene_data)
        # self._graph.add_node(rock_scene)
        # self._graph.add_edge(root, rock_scene, key=1)
        #
        # game_over_lose = make_scene(lose_data)
        # self._graph.add_node(game_over_lose)
        # self._graph.add_edge(game_over_lose, root, key=0)
        #
        # # DungeonScenes are currently constructed so the player death is the
        # #  second resolution, and the win conditions are first and third.
        # self._graph.add_edge(rock_scene, game_over_lose, key=1)
        # self._graph.add_edge(laser_scene, game_over_lose, key=1)
        #
        # game_over_win = make_scene(win_data)
        # self._graph.add_edge(game_over_win, root, key=0)
        # self._graph.add_node(game_over_win)
        #
        # self._graph.add_edge(rock_scene, laser_scene, key=0)
        # self._graph.add_edge(rock_scene, laser_scene, key=2)
        # self._graph.add_edge(laser_scene, game_over_win, key=0)
        # self._graph.add_edge(laser_scene, game_over_win, key=2)

        # self._set_current_scene(root)

    def _set_current_scene(self, scene: Scene) -> None:
        self._current_scene = scene
        ctrl, resolutions = self._current_scene.make_controller_and_resolutions()
        self._current_ctrl = ctrl

        if self._current_scene is self._root_scene:
            self._player_data = HumanoidData(Status(players.PLAYER_HEALTH),
                                             Inventory())
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

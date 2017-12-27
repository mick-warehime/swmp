from dungeon_controller import DungeonController
from decision_controller import DecisionController
import pygame as pg
from typing import Any
import networkx as nx

COMPLETE = -1


class Quest(object):
    '''An object used to organize a sequence of dungeons which create a
    quest. A quest is represented as a directed graph (DiGraph). Clients
    should only ask a quest for the next dungeon and the quest object will
    keep track of the internal state of the quest.'''

    def __init__(self,
                 screen: pg.Surface,
                 quit_func: Any) -> None:
        self._screen = screen
        self._quest_graph = self._create_quest()
        self._current = 0
        self._quit_func = quit_func
        self._current_scene = self._root_scene()

    # temporary function for creating quests - just description + filename
    def _create_quest(self) -> nx.DiGraph:
        g = nx.DiGraph()
        first_scene = QuestScene('First scene', 'goto.tmx')
        second_scene = QuestScene('Second scene', 'level1.tmx')
        g.add_edges_from([(first_scene, second_scene)])
        return g

    # find the root of the graph (first scene)
    def _root_scene(self) -> Any:
        g = self._quest_graph
        root = [n for n, d in g.in_degree() if d == 0]

        error_message = 'graph should only have 1 root, found %d'
        assert len(root) == 1, error_message % len(root)

        return root[0]

    # clients should call this method to get the next dungeon
    # either to start a quest or to get the next scene
    # returns a valid dungeon of COMPLETE if the quest is over
    def next_dungeon(self) -> DungeonController:
        if not self._current_scene:
            return COMPLETE

        tiled_map_file = self._current_scene
        self._show_intro(tiled_map_file.description)

        dungeon = self._create_dungeon()

        self._update()

        return dungeon

    # load the dungeon given a file - eventually this will be replaced
    # with a dungeon generation or load quests from files
    def _create_dungeon(self) -> DungeonController:
        map_file = self._current_scene.map_file
        return DungeonController(self._screen, map_file)

    # determine the next scene to run and set that scene as current
    # temporary - for now just grab the first neighbor of the current node
    def _update(self) -> None:
        neighbors = self._quest_graph.neighbors(self._current_scene)
        neighbors = list(neighbors)
        if len(neighbors) == 0:
            self._current_scene = None
            return

        self._current_scene = neighbors[0]

    # show the scene description - temporary - for now we just hardcode
    # a description but eventually we should use this to describe all the
    # hooks of the scene / dramatic question
    def _show_intro(self, description: str) -> None:
        screen = self._screen
        options = ['continue']
        dc = DecisionController(screen, description, options)
        dc.bind(pg.K_ESCAPE, self._quit_func)
        dc.wait_for_decision()


class QuestScene(object):
    def __init__(self, description: str, map_file: str) -> None:
        self.description = description
        self.map_file = map_file

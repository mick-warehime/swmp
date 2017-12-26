from dungeon_controller import DungeonController
from decision_controller import DecisionController
import pygame as pg
from typing import Any
import networkx as nx

COMPLETE = -1


class Quest(object):
    def __init__(self,
                 screen: pg.Surface,
                 quit_func: Any) -> None:
        self._screen = screen
        self._scene_graph = self.load_scene_graph()
        self._current = 0
        self._quit_func = quit_func
        self._current_node = self.root_scene()

    def load_scene_graph(self) -> nx.DiGraph:
        g = nx.DiGraph()
        g.add_edges_from([('goto.tmx', 'level1.tmx')])
        return g

    def root_scene(self) -> str:
        g = self._scene_graph
        root = [n for n, d in g.in_degree() if d == 0]

        error_message = 'graph should only have 1 root, found %d'
        assert len(root) == 1, error_message % len(root)

        return root[0]

    def next_dungeon(self) -> DungeonController:
        if not self._current_node:
            return COMPLETE

        tiled_map_file = self._current_node
        self.show_intro(tiled_map_file)

        dungeon = self.load_dungeon()

        self.update_node()

        return dungeon

    def load_dungeon(self) -> DungeonController:
        return DungeonController(self._screen, self._current_node)

    def update_node(self) -> None:
        neighbors = self._scene_graph.neighbors(self._current_node)
        neighbors = list(neighbors)
        if len(neighbors) == 0:
            self._current_node = None
            return

        self._current_node = neighbors[0]

    def show_intro(self, description: str) -> None:
        screen = self._screen
        options = ['continue']
        dc = DecisionController(screen, description, options)
        dc.bind(pg.K_ESCAPE, self._quit_func)
        dc.wait_for_decision()

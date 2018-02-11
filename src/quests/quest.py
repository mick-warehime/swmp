from typing import Any, List

import networkx as nx

from controller import Controller
from decision_controller import DecisionController
from dungeon_controller import DungeonController
from model import NO_RESOLUTIONS
from quests.scenes import Scene


class Quest(object):
    """An object used to organize a sequence of dungeons which create a
    quest. A quest is represented as a directed graph (DiGraph). Clients
    should only ask a quest for the next dungeon and the quest object will
    keep track of the internal state of the quest."""

    def __init__(self, quest_graph: nx.Graph = None) -> None:
        if not quest_graph:
            self._quest_graph = self._create_quest()
        else:
            self._quest_graph = quest_graph

        self._current_scene = self._root_scene()
        self._previous_scene = None
        self._is_complete = False

    # temporary function for creating quests - just description + filename
    def _create_quest(self) -> nx.DiGraph:
        g = nx.DiGraph()
        root = Decision('Kill one or two zombies?', ['one', 'two'])
        one_zombo = Dungeon('', 'level1.tmx')
        two_zombo_0 = Dungeon('', 'goto.tmx')
        g.add_edges_from([(root, one_zombo)])
        g.add_edges_from([(root, two_zombo_0)])
        two_zombo_00 = Dungeon('You kill the farther two red zombies.',
                               'level1.tmx')
        two_zombo_01 = Dungeon('You kill the closer two red zombies.',
                               'level1.tmx')
        two_zombo_02 = Dungeon('You go through the waypoint.', 'level1.tmx')
        g.add_edges_from([(two_zombo_0, two_zombo_00),
                          (two_zombo_0, two_zombo_01),
                          (two_zombo_0, two_zombo_02)])
        return g

    # find the root of the graph (first scene)
    def _root_scene(self) -> Any:
        g = self._quest_graph
        root = [n for n in g.nodes() if g.in_degree(n) == 0]

        error_message = 'graph should only have 1 root, found %d'
        assert len(root) == 1, error_message % len(root)

        return root[0]

    def next_scene(self) -> Scene:

        if self.is_complete:
            raise ValueError('Cannot get next scene of a completed quest.')

        # Initial scene
        if self._previous_scene is None:
            self._previous_scene = self._current_scene
            return self._current_scene

        # use the result of the previous scene to determine
        # the next scene
        next_index = self._current_scene.resolved_conflict_index()
        self._previous_scene = self._current_scene
        self._update_current_scene(next_index)

        if not self._current_scene:
            assert self.is_complete

        return self._current_scene

    @property
    def is_complete(self) -> bool:
        return self._is_complete

    # determine the next scene to run and set that scene as current
    # temporary - for now just grab the first neighbor of the current node
    def _update_current_scene(self, index: int) -> None:
        """Update the current scene given a resolution index.

        If NO_RESOLUTIONS is passed, the scene is unchanged.

        If the current scene does not point to other scenes,
        then self._is_complete is set to True and self._current_scene is
        cleared.

        Args:
            index: Index specifying which scene to update to.
        """
        assert self._current_scene is not None
        # quest is not over yet
        if index == NO_RESOLUTIONS:
            return

        neighbors = list(self._quest_graph.neighbors(self._current_scene))

        # quest is complete
        if len(neighbors) == 0:
            self._is_complete = True
            self._current_scene = None
            return

        self._current_scene = neighbors[index]


class Dungeon(Scene):
    def __init__(self, description: str, map_file: str) -> None:
        super().__init__(description)
        self.map_file = map_file
        self.controller: Controller = None

    def get_controller(self) -> Controller:
        if self.controller is None:
            self.controller = DungeonController(self.map_file)
        return self.controller

    # show the scene description - temporary - for now we just hardcode
    # a description but eventually we should use this to describe all the
    # hooks of the scene / dramatic question
    def show_intro(self) -> None:
        if not self.description:
            return
        options = ['continue']
        dc = DecisionController(self.description, options)
        dc.wait_for_decision()


class Decision(Scene):
    def __init__(self, description: str, options: List[str]) -> None:
        super().__init__(description)
        self.options = options

    def get_controller(self) -> Controller:
        if self.controller is None:
            self.controller = DecisionController(self.description,
                                                 self.options)
        return self.controller

    def show_intro(self) -> None:
        if self.controller:
            self.controller.wait_for_decision()
        else:
            raise Exception('call get_controller() first')



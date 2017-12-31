from dungeon_controller import DungeonController
from decision_controller import DecisionController
from controller import Controller
from model import NO_RESOLUTIONS
from typing import Any, List
import networkx as nx

COMPLETE = -1


class Quest(object):
    '''An object used to organize a sequence of dungeons which create a
    quest. A quest is represented as a directed graph (DiGraph). Clients
    should only ask a quest for the next dungeon and the quest object will
    keep track of the internal state of the quest.'''

    def __init__(self, quest_graph: nx.Graph = None) -> None:
        if not quest_graph:
            self._quest_graph = self._create_quest()
        else:
            self._quest_graph = quest_graph
        self._current = 0
        self._current_scene = self._root_scene()
        self._previous_scene = None

    # temporary function for creating quests - just description + filename
    def _create_quest(self) -> nx.DiGraph:
        g = nx.DiGraph()
        root = Decision('Kill one or two zombies?', ['one', 'two'])
        two_zombo = Dungeon('', 'goto.tmx')
        one_zombo = Dungeon('', 'level1.tmx')
        g.add_edges_from([(root, one_zombo)])
        g.add_edges_from([(root, two_zombo)])
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
    def next_scene(self) -> Any:

        # use the result of the previous scene to determine
        # the next scene
        if self._previous_scene:
            next_index = self._previous_scene.resolved_conflict_index()
            self._previous_scene = self._current_scene
            self.update_scene(next_index)
        else:
            self._previous_scene = self._current_scene

        if not self._current_scene:
            return COMPLETE

        return self._current_scene

    # determine the next scene to run and set that scene as current
    # temporary - for now just grab the first neighbor of the current node
    def update_scene(self, index: int) -> None:
        # quest is not over yet
        if not self._current_scene or index == NO_RESOLUTIONS:
            return

        neighbors = self._quest_graph.neighbors(self._current_scene)
        neighbors = list(neighbors)

        # quest is complete
        if len(neighbors) == 0:
            self._current_scene = None
            return

        self._current_scene = neighbors[index]


class Scene(object):
    def __init__(self, description: str) -> None:
        self.description = description
        self.controller = None

    def show_intro(self) -> None:
        raise NotImplementedError()

    def get_controller(self) -> Controller:
        raise NotImplementedError()

    def resolved_conflict_index(self) -> int:
        if self.controller:
            return self.controller.resolved_conflict_index()
        raise Exception('call get_controller() first')


class Dungeon(Scene):
    def __init__(self, description: str, map_file: str) -> None:
        super().__init__(description)
        self.map_file = map_file
        self.controller: Controller = None

    def get_controller(self) -> Controller:
        self.controller = DungeonController(self.map_file)
        return self.controller

    # show the scene description - temporary - for now we just hardcode
    # a description but eventually we should use this to describe all the
    # hooks of the scene / dramatic question
    def show_intro(self) -> None:
        if self.description in '':
            return
        options = ['continue']
        dc = DecisionController(self.description, options)
        dc.wait_for_decision()


class Decision(Scene):
    def __init__(self, description: str, options: List[str]) -> None:
        super().__init__(description)
        self.options = options

    def get_controller(self) -> Controller:
        self.controller = DecisionController(self.description, self.options)
        return self.controller

    def show_intro(self) -> None:
        if self.controller:
            self.controller.wait_for_decision()
        else:
            raise Exception('call get_controller() first')

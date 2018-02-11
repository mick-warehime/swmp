import unittest
from quests.quest import Quest, Dungeon, Decision
import networkx as nx

from test.pygame_mock import initialize_pygame


def setUpModule() -> None:
    initialize_pygame()


def test_graph_dungeons() -> nx.Graph:
    g = nx.DiGraph()
    level = 'level1.tmx'
    root = Dungeon('root', level)
    s0 = Dungeon('0', level)
    s00 = Dungeon('00', level)
    s01 = Dungeon('01', level)
    s1 = Dungeon('1', level)
    s10 = Dungeon('10', level)
    s11 = Dungeon('11', level)
    final = Dungeon('final', level)
    edges = [(root, s0), (root, s1), (s0, s00), (s0, s01),
             (s1, s10), (s1, s11), (s00, final), (s01, final),
             (s10, final), (s11, final)]
    g.add_edges_from(edges)
    return g


def test_graph_decisions() -> nx.Graph:
    g = nx.DiGraph()
    options = ['0', '1']
    root = Decision('root', options)
    s0 = Decision('0', options)
    s00 = Decision('00', options)
    s01 = Decision('01', options)
    s1 = Decision('1', options)
    s10 = Decision('10', options)
    s11 = Decision('11', options)
    final = Decision('final', options)
    edges = [(root, s0), (root, s1), (s0, s00), (s0, s01),
             (s1, s10), (s1, s11), (s00, final), (s01, final),
             (s10, final), (s11, final)]
    g.add_edges_from(edges)
    return g


def test_graph_mixed() -> nx.Graph:
    g = nx.DiGraph()
    options = ['0', '1']
    level = 'level1.tmx'
    root = Decision('root', options)
    s0 = Dungeon('0', level)
    s00 = Dungeon('00', level)
    s01 = Dungeon('01', level)
    s1 = Decision('1', options)
    s10 = Decision('10', options)
    s11 = Decision('11', options)
    final = Dungeon('final', level)
    edges = [(root, s0), (root, s1), (s0, s00), (s0, s01),
             (s1, s10), (s1, s11), (s00, final), (s01, final),
             (s10, final), (s11, final)]
    g.add_edges_from(edges)
    return g


def resolve_conflict_with_index(q: Quest, index: int) -> Quest:
    q._current_scene.resolved_conflict_index = lambda: index


class QuestTest(unittest.TestCase):
    pass
    # def test_quest_init(self) -> None:
    #     q = Quest()
    #     self.assertTrue(q is not None)
    #
    # def test_quest_update_node(self) -> None:
    #     q = Quest()
    #
    #     scene_1 = q.next_scene()
    #     scene_1.get_controller()
    #
    #     # fake resolving a conflict
    #     resolve_conflict_with_index(q, 0)
    #
    #     scene_2 = q.next_scene()
    #     self.assertNotEqual(scene_1, scene_2)
    #
    # def test_multiple_conflicts(self) -> None:
    #     # there are four paths through the graph
    #     paths = [(0, 0), (0, 1), (1, 0), (1, 1)]
    #     for first, second in paths:
    #         q = Quest(test_graph_dungeons())
    #
    #         scene_1 = q.next_scene()
    #         self.assertEqual(scene_1.description, 'root')
    #
    #         # fake resolve first conflict
    #         resolve_conflict_with_index(q, first)
    #
    #         scene_2 = q.next_scene()
    #         self.assertEqual(scene_2.description, str(first))
    #
    #         # fake resolve second conflict
    #         resolve_conflict_with_index(q, second)
    #
    #         scene_3 = q.next_scene()
    #         self.assertEqual(scene_3.description, str(first) + str(second))
    #
    #         # fake resolve third
    #         resolve_conflict_with_index(q, 0)
    #
    #         scene_4 = q.next_scene()
    #         self.assertEqual(scene_4.description, 'final')
    #
    # def test_dungeon_and_decision(self) -> None:
    #     # there are four paths through the graph
    #     paths = [(0, 0), (0, 1), (1, 0), (1, 1)]
    #     for first, second in paths:
    #         q = Quest(test_graph_mixed())
    #
    #         scene_1 = q.next_scene()
    #         self.assertEqual(scene_1.description, 'root')
    #
    #         # fake resolve first conflict
    #         resolve_conflict_with_index(q, first)
    #
    #         scene_2 = q.next_scene()
    #         self.assertEqual(scene_2.description, str(first))
    #
    #         # fake resolve second conflict
    #         resolve_conflict_with_index(q, second)
    #
    #         scene_3 = q.next_scene()
    #         self.assertEqual(scene_3.description, str(first) + str(second))
    #
    #         # fake resolve third
    #         resolve_conflict_with_index(q, 0)
    #
    #         scene_4 = q.next_scene()
    #         self.assertEqual(scene_4.description, 'final')
    #
    # def test_multiple_decisions(self) -> None:
    #     # there are four paths through the graph
    #     paths = [(0, 0), (0, 1), (1, 0), (1, 1)]
    #     for first, second in paths:
    #         q = Quest(test_graph_decisions())
    #
    #         scene_1 = q.next_scene()
    #         self.assertEqual(scene_1.description, 'root')
    #
    #         # fake resolve first conflict
    #         resolve_conflict_with_index(q, first)
    #
    #         scene_2 = q.next_scene()
    #         self.assertEqual(scene_2.description, str(first))
    #
    #         # fake resolve second conflict
    #         resolve_conflict_with_index(q, second)
    #
    #         scene_3 = q.next_scene()
    #         self.assertEqual(scene_3.description, str(first) + str(second))
    #
    #         # fake resolve third
    #         resolve_conflict_with_index(q, 0)
    #
    #         scene_4 = q.next_scene()
    #         self.assertEqual(scene_4.description, 'final')

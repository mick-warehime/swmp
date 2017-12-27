import unittest
import quest
from typing import Any


def show_intro(self: Any, filename: str) -> None:
    pass


def load_dungeon(self: Any) -> Any:
    pass


class QuestTest(unittest.TestCase):
    def setUp(self) -> None:
        self.Quest = quest.Quest
        self.Quest.show_intro = show_intro
        self.Quest.load_dungeon = load_dungeon

    def test_quest_init(self) -> None:
        q = self.Quest(None, None)
        self.assertTrue(q is not None)

    def test_quest_update_node(self) -> None:
        q = self.Quest(None, None)
        node_i = q._current_node
        q.next_dungeon()
        node_f = q._current_node
        self.assertNotEqual(node_i, node_f)

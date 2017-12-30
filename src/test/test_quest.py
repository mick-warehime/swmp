import unittest
import quest
from typing import Any


def _show_intro(self: Any, filename: str) -> None:
    pass


def _create_dungeon(self: Any) -> Any:
    pass


class QuestTest(unittest.TestCase):
    def setUp(self) -> None:
        self.Quest = quest.Quest
        self.Quest._show_intro = _show_intro
        self.Quest._create_dungeon = _create_dungeon

    def test_quest_init(self) -> None:
        q = self.Quest()
        self.assertTrue(q is not None)

    def test_quest_update_node(self) -> None:
        q = self.Quest()
        node_i = q._current_scene
        q.next_dungeon()
        node_f = q._current_scene
        self.assertNotEqual(node_i, node_f)

import unittest
import quest


class QuestTest(unittest.TestCase):
    def test_quest_init(self) -> None:
        q = quest.Quest(None, None)
        self.assertTrue(q is not None)

    # def test_quest_update_node(self) -> None:
    #     q = quest.Quest(None, None)
    #     node_i = q._current_node
    #     q.next_dungeon()
    #     node_f = q._current_node
    #     self.assertNotEqual(node_i, node_f)


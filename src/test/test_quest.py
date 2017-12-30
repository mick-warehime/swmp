import unittest
from quest import Quest


class QuestTest(unittest.TestCase):
    def test_quest_init(self) -> None:
        q = Quest()
        self.assertTrue(q is not None)

    def test_quest_update_node(self) -> None:
        q = Quest()

        scene_1 = q.next_scene()
        scene_1.get_controller()
        # fake resolving a conflict
        scene_1.resolved_conflict_index = lambda: 0

        scene_2 = q.next_scene()
        self.assertNotEqual(scene_1, scene_2)

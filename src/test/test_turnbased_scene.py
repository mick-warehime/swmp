from unittest import TestCase
from data.input_output import load_quest_data
from quests.quest import Quest


class TestTurnBasedScene(TestCase):

    def test_create_scene(self) -> None:
        quest_data = load_quest_data('test_turnbased')
        self.quest_graph = Quest(quest_data)

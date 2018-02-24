import unittest
from typing import Dict, Any

from controllers.base import initialize_controller
from quests.quest import Quest
from test.pygame_mock import initialize_pygame


def setUpModule() -> None:
    initialize_pygame()
    initialize_controller(None, None)

    root_data = {'type': 'decision',
                 'description': 'Lasers or rocks?',
                 'choices': [
                     {'one': {'description': 'rocks',
                              'next scene': 'rock'}},
                     {'two': {'description': 'lose?',
                              'next scene': 'lose'}}
                 ]}
    rock_data = {'type': 'decision',
                 'description': 'One or two?',
                 'choices': [
                     {'one': {'description': 'One please',
                              'next scene':'rock' }},
                     {'two': {'description': 'two!',
                              'next scene': 'lose'}}]}
    lose_data = {'type': 'decision',
                 'description': 'You lose',
                 'choices': [
                     {'one': {'description': 'play again?',
                              'next scene': 'root'}}]}

    QuestTest.simple_quest_data = {'root': root_data,
                                   'rock': rock_data,
                                   'lose': lose_data}


    # TODO(dvirk): Add tests.


class QuestTest(unittest.TestCase):
    simple_quest_data: Dict[str, Any] = None

    def test_init_simple_quest(self) -> None:
        quest = Quest(self.simple_quest_data)

    def test_init_no_root_error(self) -> None:
        bad_quest_data = self.simple_quest_data.copy()
        bad_quest_data.pop('root')
        bad_quest_data['lose'] = {'type': 'decision',
                                  'description': 'You lose',
                                  'choices': [
                                      {'again': {'description': 'play again',
                                                 'next scene': 'rock'}}]}
        with self.assertRaisesRegex(KeyError, 'exactly one scene'):
            Quest(bad_quest_data)

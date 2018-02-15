import unittest

from controller import initialize_controller
from quests.quest import Quest
from test.pygame_mock import initialize_pygame


def setUpModule() -> None:
    initialize_pygame()
    initialize_controller(None, None)


root_data = {'type': 'decision',
             'prompt': 'Lasers or rocks?',
             'choices': [{'lasers please': 'lose'},
                         {'rocks!': 'rock'}]}
rock_data = {'type': 'decision',
             'prompt': 'One or two?',
             'choices': [{'One please': 'rock'},
                         {'two!': 'lose'}]}
lose_data = {'type': 'decision',
             'prompt': 'You lose',
             'choices': [{'play again?': 'root'}]}

simple_quest_data = {'root': root_data,
                     'rock': rock_data,
                     'lose': lose_data}


# TODO(dvirk): Add tests.
class QuestTest(unittest.TestCase):
    @staticmethod
    def test_init_simple_quest():
        quest = Quest(simple_quest_data)

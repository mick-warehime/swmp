import unittest
# from quests.quest import Quest

from test.pygame_mock import initialize_pygame


def setUpModule() -> None:
    initialize_pygame()


root_data = {'type': 'decision',
             'prompt': 'Lasers or rocks?',
             'choices': [{'lasers please': 'laser scene'},
                         {'rocks!': 'rock scene'}]}
rock_data = {'type': 'decision',
             'prompt': 'Lasers or rocks?',
             'choices': [{'lasers please': 'laser scene'},
                         {'rocks!': 'rock scene'}]}

simple_quest_data = {'root': root_data}

# TODO(dvirk): Add tests.
class QuestTest(unittest.TestCase):
    pass

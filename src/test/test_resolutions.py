import unittest

from model import Groups
from quests import resolutions
from test import pygame_mock, testing_utilities

import test.dummy_audio_video


def setUpModule() -> None:
    pygame_mock.initialize_pygame()

    groups = Groups()
    timer = pygame_mock.MockTimer()
    pygame_mock.initialize_gameobjects(groups, timer)


class ResolutionsTest(unittest.TestCase):
    def test_kill_group_starts_resolved(self) -> None:
        kill_group = resolutions.KillGroup('Mortys')
        self.assertTrue(kill_group.is_resolved)

    def test_kill_group_resolved_after_death(self) -> None:
        kill_group = resolutions.KillGroup('Mortys')
        player = testing_utilities.make_player()
        sprite_labels = {'Mortys': {player}}

        kill_group.load_sprite_data(sprite_labels)

        self.assertFalse(kill_group.is_resolved)

        player.kill()
        self.assertTrue(kill_group.is_resolved)

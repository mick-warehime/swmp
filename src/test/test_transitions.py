import unittest

from controllers.transition_controller import TransitionController
from data import constructors
from items import ItemObject
from model import Groups
from quests.resolutions import MakeDecision
from quests.scenes.transitions import TransitionScene
from test import pygame_mock
from test.testing_utilities import make_player


def setUpModule() -> None:
    TransitionControllerTest.groups = Groups()
    pygame_mock.initialize_everything(TransitionControllerTest.groups)


class TransitionControllerTest(unittest.TestCase):
    groups: Groups = None

    def tearDown(self) -> None:
        self.groups.empty()

    def test_set_player_adds_gained_item(self) -> None:
        description = 'description'
        decision = MakeDecision('decision')

        rock: ItemObject = constructors.build_map_object('rock')

        player = make_player()

        self.assertNotIn(rock.mod.loc, player.inventory.active_mods)
        ctrl = TransitionController(description, decision, rock)
        self.assertNotIn(rock.mod.loc, player.inventory.active_mods)
        ctrl.set_player_data(player.data)
        self.assertIn(rock.mod.loc, player.inventory.active_mods)

    def test_set_player_gained_item_removed_from_groups_even_if_not_picked_up(
            self) -> None:
        transition = TransitionScene('description', 'shotgun')

        player = make_player()

        while not player.inventory.backpack.is_full:
            pistol = constructors.build_map_object('pistol')
            player.inventory.attempt_pickup(pistol)

        num_items = len(self.groups.items)
        ctrl, _ = transition.make_controller_and_resolutions()
        self.assertEqual(len(self.groups.items), num_items + 1)
        ctrl.set_player_data(player.data)
        self.assertEqual(len(self.groups.items), num_items)

        shotgun = constructors.build_map_object('shotgun')
        self.assertNotIn(shotgun.mod, player.inventory.backpack)
        active_mod = player.inventory.active_mods[shotgun.mod.loc]
        self.assertNotEqual(shotgun.mod, active_mod)

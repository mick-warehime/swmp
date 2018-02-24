import unittest

from parameterized import parameterized
from pygame import K_SPACE

import controllers.base
from controllers import keyboards
from controllers.skill_check_controller import DifficultyRating, \
    SkillCheckController
from creatures.humanoids import HumanoidData, Status, Inventory
from quests.resolutions import MakeDecision
from quests.scenes.skill_checks import SkillCheckScene
from test import pygame_mock


def setUpModule() -> None:
    controllers.base.initialize_controller(None, lambda x: x)


class SkillCheckControllerTest(unittest.TestCase):
    space_key = K_SPACE

    def setUp(self) -> None:
        pg = pygame_mock.Pygame()
        controllers.base.pg.mouse = pg.mouse
        controllers.base.pg.key = pg.key

    def tearDown(self) -> None:
        controllers.base.Controller.keyboard.handle_input()

    def test_skill_check_controller_starts_unresolved(self)->None:
        success = MakeDecision('success')
        failure = MakeDecision('failure')
        rating = DifficultyRating.MEDIUM
        ctrl = SkillCheckController(success, failure, rating)

        self.assertFalse(success.is_resolved)
        self.assertFalse(failure.is_resolved)

    def test_skill_check_controller_unresolved_after_update(self)->None:
        success = MakeDecision('success')
        failure = MakeDecision('failure')
        rating = DifficultyRating.MEDIUM
        ctrl = SkillCheckController(success, failure, rating)

        player_data = HumanoidData(Status(10), Inventory())
        ctrl.set_player_data(player_data)
        ctrl.update()

        self.assertFalse(success.is_resolved)
        self.assertFalse(failure.is_resolved)

    def test_skill_check_controller_one_resolves_after_space(self)->None:
        success = MakeDecision('success')
        failure = MakeDecision('failure')
        rating = DifficultyRating.MEDIUM
        ctrl = SkillCheckController(success, failure, rating)

        player_data = HumanoidData(Status(10), Inventory())
        ctrl.set_player_data(player_data)

        keyboards.pg.key.pressed[self.space_key] = 1

        ctrl.update()

        one_resolved = success.is_resolved + failure.is_resolved % 2
        self.assertTrue(one_resolved)

    cases = [(k,) for k in range(50)]

    @parameterized.expand(cases)
    def test_skill_check_controller_impossible_never_success(
            self, case: int) -> None:
        success = MakeDecision('success')
        failure = MakeDecision('failure')
        rating = DifficultyRating.IMPOSSIBLE
        ctrl = SkillCheckController(success, failure, rating)

        player_data = HumanoidData(Status(10), Inventory())
        ctrl.set_player_data(player_data)

        keyboards.pg.key.pressed[self.space_key] = 1

        ctrl.update()

        one_resolved = success.is_resolved + failure.is_resolved % 2
        self.assertTrue(one_resolved)
        self.assertTrue(failure.is_resolved)
        keyboards.pg.key.pressed[self.space_key] = 0

    def test_skill_check_scene_typical_behavior(self) -> None:
        success_data = {'description': 'success!'}
        failure_data = {'description': 'failure!'}

        scene = SkillCheckScene(success_data, failure_data, 'easy')
        ctrl, resolutions = scene.make_controller_and_resolutions()

        player_data = HumanoidData(Status(10), Inventory())
        ctrl.set_player_data(player_data)

        keyboards.pg.key.pressed[self.space_key] = 1

        ctrl.update()

        one_resolved = sum(res.is_resolved for res in resolutions) % 2
        self.assertTrue(one_resolved)
        keyboards.pg.key.pressed[self.space_key] = 0


if __name__ == '__main__':
    unittest.main()

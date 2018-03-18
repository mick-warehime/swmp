from enum import Enum
from random import random

import pygame as pg

from controllers import base
from creatures.humanoids import HumanoidData
from quests.resolutions import MakeDecision
from view.decision_view import DecisionView


class DifficultyRating(Enum):
    TRIVIAL = 'trivial'
    VERY_EASY = 'very easy'
    EASY = 'easy'
    MEDIUM = 'medium'
    HARD = 'hard'
    VERY_HARD = 'very hard'
    IMPOSSIBLE = 'impossible'

    @property
    def success_probability(self) -> float:
        return _rating_probability_map[self]


_rating_probability_map = {DifficultyRating.TRIVIAL: 1.0,
                           DifficultyRating.VERY_EASY: 0.875,
                           DifficultyRating.EASY: 0.75,
                           DifficultyRating.MEDIUM: 0.5,
                           DifficultyRating.HARD: 0.25,
                           DifficultyRating.VERY_HARD: 0.125,
                           DifficultyRating.IMPOSSIBLE: 0}


class SkillCheckController(base.Controller):
    """Handles interaction between user, view, and the skill check."""

    def __init__(self, success: MakeDecision, failure: MakeDecision,
                 rating: DifficultyRating) -> None:
        super().__init__()
        self._skill_check = SkillCheck(success, failure, rating)

        self._view: DecisionView = None
        self._player_data: HumanoidData = None
        self._allowed_keys = [pg.K_SPACE, pg.K_ESCAPE]
        self._resolved = False

    def draw(self) -> None:
        assert self._view is not None, 'update must be called before draw.'
        self._view.draw()

    def update(self) -> None:
        assert self._player_data is not None, 'cannot update before ' \
                                              'player_data is set.'

        if not self._resolved:
            resolution = self._skill_check.resolve(self._player_data)
            description = resolution.description
            self._view = DecisionView(description, ['press space to continue'],
                                      enumerate_options=False)
            self.keyboard.bind_on_press(pg.K_SPACE, resolution.choose)
            self._resolved = True

        self.keyboard.handle_input(self._allowed_keys)

    def set_player_data(self, data: HumanoidData) -> None:
        self._player_data = data


class SkillCheck(object):
    """Uses player data to decide between different resolutions"""

    def __init__(self, success: MakeDecision, failure: MakeDecision,
                 rating: DifficultyRating) -> None:
        self._success = success
        self._failure = failure
        self._rating = rating

    def resolve(self, data: HumanoidData) -> MakeDecision:
        success_prob = self._rating.success_probability

        if random() < success_prob:
            return self._success
        else:
            return self._failure

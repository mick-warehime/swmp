from dungeon_controller import DungeonController
from decision_controller import DecisionController
import pygame as pg
from typing import List, Any

COMPLETE = -1


class Quest(object):
    def __init__(self,
                 screen: pg.Surface,
                 quit_func: Any) -> None:
        self._screen = screen
        self._scenes: List[Any] = []
        self._current = 0
        self._quit_func = quit_func

    def next(self) -> DungeonController:
        if self._current > 2:
            return COMPLETE

        description = 'level %d - find the exit'
        descr_i = description % self._current

        self._current += 1
        self.show_intro(descr_i)

        dungeon = DungeonController(self._screen, 'goto.tmx')

        return dungeon

    def show_intro(self, description: str) -> None:
        screen = self._screen
        options = ['continue']
        dc = DecisionController(screen, description, options)
        dc.bind(pg.K_ESCAPE, self._quit_func)
        dc.wait_for_decision()

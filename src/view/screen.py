import pygame as pg

import settings


class ScreenAccess(object):
    """Label for an object with access to the screen."""

    _screen: pg.Surface = None

    def __init__(self) -> None:
        if self._screen is None:
            raise RuntimeError('ScreenAccess not initialized.')

    @classmethod
    def initialize(cls, screen: pg.Surface = None) -> None:
        if cls._screen is not None:
            return

        if screen is None:
            screen = pg.display.set_mode((settings.WIDTH, settings.HEIGHT))
        cls._screen = screen

    @property
    def screen(self) -> pg.Surface:
        return self._screen

import abc

import pygame as pg

import settings
from model import GroupsAccess
from view.camera import Camera
from view.draw_utils import rect_on_screen
from view.screen import ScreenAccess


class DrawEffect(abc.ABC, ScreenAccess, GroupsAccess):
    """Interface for an object with a draw method.
    Has access to a Camera, the screen, and Groups."""

    _camera: Camera = None

    def __init__(self) -> None:
        if self._camera is None:
            raise RuntimeError('Must first call DrawEffect.set_camera()')
        ScreenAccess.__init__(self)
        GroupsAccess.__init__(self)

    @classmethod
    def set_camera(cls, camera: Camera) -> None:
        cls._camera = camera

    @property
    def camera(self) -> Camera:
        return self._camera

    @abc.abstractmethod
    def draw(self):
        """Draw method"""


class DrawDebugRects(DrawEffect):
    def draw(self):
        for sprite in self.groups.all_sprites:
            if hasattr(sprite, 'motion'):
                rect = sprite.motion.hit_rect
            else:
                rect = sprite.rect
            shifted_rect = self.camera.shift_by_topleft(rect)
            if rect_on_screen(self.screen, shifted_rect):
                pg.draw.rect(self.screen, settings.CYAN, shifted_rect, 1)
        for obstacle in self.groups.walls:
            assert obstacle not in self.groups.all_sprites
            shifted_rect = self.camera.shift_by_topleft(obstacle.rect)
            if rect_on_screen(self.screen, shifted_rect):
                pg.draw.rect(self.screen, settings.CYAN, shifted_rect, 1)

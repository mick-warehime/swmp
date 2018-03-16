from typing import Any

import pygame as pg
from pygame.math import Vector2

import images
from model import GameObject
from settings import TILESIZE


class Waypoint(GameObject):
    _image = None

    def __init__(self, pos: Vector2, player: Any) -> None:
        super().__init__(pos)
        self._rect = self.image.get_rect().copy()
        self._rect.center = pos
        self.player = player

        waypointgroups = [self.groups.all_sprites]

        pg.sprite.Sprite.__init__(self, waypointgroups)

    @property
    def image(self) -> pg.Surface:
        if Waypoint._image is None:
            img = images.get_image(images.WAYPOINT_IMG)
            Waypoint._image = pg.transform.scale(img, (TILESIZE, TILESIZE))
        return self._image

    @property
    def rect(self) -> pg.Rect:
        return self._rect

from typing import Any

import pygame as pg
from pygame.math import Vector2
from pygame.sprite import Group

import images
from model import DynamicObject
from settings import TILESIZE


class Waypoint(DynamicObject):
    _image = None

    def __init__(self, pos: Vector2, player: Any,
                 conflict_group: Group) -> None:
        super().__init__(pos)
        self._rect = self.image.get_rect().copy()
        self._rect.center = pos
        self.player = player

        if conflict_group is None:
            raise ValueError('missing conflict for waypoint at %s', str(pos))

        waypoint_groups = [self._groups.all_sprites,
                           self._groups.items,
                           conflict_group]

        pg.sprite.Sprite.__init__(self, waypoint_groups)

    def update(self) -> None:
        if self.rect.colliderect(self.player.rect):
            self.kill()

    @property
    def image(self) -> pg.Surface:
        if Waypoint._image is None:
            img = images.get_image(images.WAYPOINT_IMG)
            Waypoint._image = pg.transform.scale(img, (TILESIZE, TILESIZE))
        return self._image

    @property
    def rect(self) -> pg.Rect:
        return self._rect

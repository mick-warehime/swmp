import pygame as pg
from typing import Tuple
import model as mdl
import random
import images
from pygame.math import Vector2


class PartyMember(mdl.GameObject):
    COUNT = 1

    def __init__(self, pos: Vector2):
        super().__init__(pos)
        self.initiative = 0
        self.member_number = PartyMember.COUNT
        PartyMember.COUNT += 1

        self._base_rect = self.image.get_rect().copy()

    def prepare_combat(self) -> int:
        return random.randint(0, 20)

    @property
    def image(self) -> pg.Surface:
        return images.party_member_image(self.member_number)

    @property
    def rect(self) -> pg.Rect:
        """Rect object used in sprite collisions."""
        self._base_rect.center = self.pos
        return self._base_rect

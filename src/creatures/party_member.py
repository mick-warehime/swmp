import pygame as pg
import model as mdl
import random
from view import images
from pygame.math import Vector2


class PartyMember(mdl.GameObject):
    COUNT = 1

    def __init__(self, pos: Vector2) -> None:
        super().__init__(pos)
        self.initiative = 0
        self.member_number = PartyMember.COUNT
        PartyMember.COUNT += 1

        self._base_rect = self.image.get_rect().copy()
        self.speed = self.member_number + 4

    def prepare_combat(self) -> int:
        self.initiative = random.randint(0, 20)
        return self.initiative

    @property
    def image(self) -> pg.Surface:
        return images.party_member_image(self.member_number)

    @property
    def rect(self) -> pg.Rect:
        """Rect object used in sprite collisions."""
        self._base_rect.center = self.pos
        return self._base_rect

    def can_reach(self, x: int, y: int) -> bool:
        return (x ** 2 + y ** 2) < (self.speed - 1) ** 2

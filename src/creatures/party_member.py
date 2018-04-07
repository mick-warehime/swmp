import pygame as pg
import model as mdl
import random
from pygame.math import Vector2


class PartyMember(mdl.GameObject):

    def __init__(self, pos: Vector2, image: pg.Surface, speed: int) -> None:
        super().__init__(pos)
        self.initiative = 0
        self._image = image
        self._base_rect = self.image.get_rect().copy()
        self.speed = speed

    def prepare_combat(self) -> int:
        self.initiative = random.randint(0, 20)
        return self.initiative

    @property
    def rect(self) -> pg.Rect:
        """Rect object used in sprite collisions."""
        self._base_rect.center = self.pos
        return self._base_rect

    @property
    def image(self) -> pg.Surface:
        return self._image

    def can_reach(self, x: int, y: int) -> bool:
        return (x ** 2 + y ** 2) <= self.speed ** 2

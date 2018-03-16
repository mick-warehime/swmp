import math
from typing import Tuple

import pygame as pg
from pygame.math import Vector2

import images
from creatures.humanoids import Humanoid, EnergySource

PLAYER_HEALTH = 100
PLAYER_SPEED = 280
PLAYER_ROT_SPEED = 200
PLAYER_HIT_RECT = pg.Rect(0, 0, 35, 35)
PLAYER_MAX_ENERGY = 100.0
PLAYER_ENERGY_RECHARGE = 5.0

DAMAGE_ALPHA = list(range(0, 255, 55))


class Player(Humanoid):
    def __init__(self, pos: Vector2) -> None:
        super().__init__(PLAYER_HIT_RECT, pos, PLAYER_HEALTH)
        pg.sprite.Sprite.__init__(self, self._groups.all_sprites)

        self._mouse_pos = (0, 0)

        self.energy_source = EnergySource(PLAYER_MAX_ENERGY,
                                          PLAYER_ENERGY_RECHARGE)

    def move_towards_mouse(self) -> None:
        self._rotate_towards_cursor()

        closest_approach = 10
        if self._distance_to_mouse() < closest_approach:
            return

        self._step_forward()

    @property
    def image(self) -> pg.Surface:
        base_image = images.get_image(images.PLAYER_IMG)
        return pg.transform.rotate(base_image, self.motion.rot)

    # translate_direction = slide in that direction
    def translate_up(self) -> None:
        self.motion.vel += Vector2(0, -PLAYER_SPEED)

    def translate_down(self) -> None:
        self.motion.vel += Vector2(0, PLAYER_SPEED)

    def translate_right(self) -> None:
        self.motion.vel += Vector2(PLAYER_SPEED, 0)

    def translate_left(self) -> None:
        self.motion.vel += Vector2(-PLAYER_SPEED, 0)

    # step_direction - rotates player towards the current direction
    # and then takes a step relative to that direction
    def _step_forward(self) -> None:
        self.motion.vel += Vector2(PLAYER_SPEED, 0).rotate(-self.motion.rot)

    def update(self) -> None:
        self._rotate_towards_cursor()

        self.motion.update()
        self.energy_source.passive_recharge(self.timer.dt)

        # reset the movement after each update
        self.motion.vel = Vector2(0, 0)

    def set_mouse_pos(self, pos: Tuple[int, int]) -> None:
        self._mouse_pos = pos

    def _distance_to_mouse(self) -> float:
        x = self._mouse_pos[0] - self.pos[0]
        y = self._mouse_pos[1] - self.pos[1]

        return math.sqrt(x ** 2 + y ** 2)

    def _rotate_towards_cursor(self) -> None:
        x = self._mouse_pos[0] - self.pos[0]
        y = self._mouse_pos[1] - self.pos[1]

        angle = -(90 - math.atan2(x, y) * 180 / math.pi) % 360

        self.motion.rot = int(angle % 360)

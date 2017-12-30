from pygame.math import Vector2
from pygame.rect import Rect
from pygame.surface import Surface
from pygame.transform import rotate, scale

import images
from weapons import Projectile


class LaserBolt(Projectile):
    max_lifetime: int = 1000
    speed: int = 1000
    damage: int = 100

    def __init__(self, pos: Vector2, direction: Vector2) -> None:
        # Since the bold is long and wide, I am approximating its rect by a
        # square.
        image = images.get_image(images.LASER_BOLT).copy()
        image = scale(image, (30, 3))
        assert direction.is_normalized()
        angle = direction.angle_to(Vector2(0, 0))
        self._base_image = rotate(image, angle)

        super().__init__(pos, direction, False)

        self._base_rect = Rect(0, 0, 10, 10)

    @property
    def image(self) -> Surface:
        return self._base_image

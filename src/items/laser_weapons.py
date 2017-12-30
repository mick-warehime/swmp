from pygame.math import Vector2
from pygame.rect import Rect
from pygame.surface import Surface
from pygame.transform import rotate, scale

import images
import sounds
from abilities import FireProjectile
from weapons import Projectile


class LaserBolt(Projectile):
    max_lifetime: int = 1000
    speed: int = 1000
    damage: int = 100

    def __init__(self, pos: Vector2, direction: Vector2) -> None:
        image = images.get_image(images.LASER_BOLT).copy()
        image = scale(image, (30, 3))
        angle = direction.angle_to(Vector2(0, 0))
        self._base_image = rotate(image, angle)

        super().__init__(pos, direction, False)

        # Since the bold is long and wide, I am approximating its rect by a
        # square.
        self._base_rect = Rect(0, 0, 10, 10)

    @property
    def image(self) -> Surface:
        return self._base_image


class ShootLaser(FireProjectile):
    _kickback = 0
    _cool_down_time = 500
    _spread = 10
    _projectile_count = 5
    _make_projectile = LaserBolt

    def __init__(self) -> None:
        super().__init__()
        self.uses_left = 1

    def _fire_effects(self, origin: Vector2) -> None:
        sounds.play('grunt')
        self.uses_left -= 1

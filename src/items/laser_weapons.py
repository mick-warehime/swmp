from pygame import transform

from pygame.math import Vector2
from pygame.rect import Rect
from pygame.surface import Surface
from pygame.transform import rotate, scale

import images
import sounds
from abilities import FireProjectile, Ability
from mods import Mod, ModLocation, ItemObject
from tilemap import ObjectType
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
    _spread = 2
    _projectile_count = 1
    _make_projectile = LaserBolt

    def __init__(self) -> None:
        super().__init__()

    def _fire_effects(self, origin: Vector2) -> None:
        sounds.fire_weapon_sound(ObjectType.LASER_GUN)


class LaserMod(Mod):
    loc = ModLocation.ARMS

    def __init__(self) -> None:
        self._ability = ShootLaser()

    @property
    def ability(self) -> Ability:
        return self._ability

    @property
    def expended(self) -> bool:
        return False

    @property
    def stackable(self) -> bool:
        return False

    @property
    def equipped_image(self) -> Surface:
        return images.get_image(images.LASER_BOLT)

    @property
    def backpack_image(self) -> Surface:
        return transform.scale(images.get_image(images.LASER_GUN), (30, 30))


class LaserGun(ItemObject):
    gun_size = (30, 16)

    def __init__(self, pos: Vector2) -> None:
        self._check_class_initialized()
        mod = LaserMod()
        image = images.get_image(images.LASER_GUN)
        self._image = transform.scale(image, self.gun_size)

        super().__init__(mod, pos)

    @property
    def image(self) -> Surface:
        return self._image

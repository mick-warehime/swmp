from typing import List

from pygame import transform

from pygame.math import Vector2
from pygame.rect import Rect
from pygame.surface import Surface
from pygame.transform import rotate, scale

import images
import sounds
from abilities import FireProjectile, Ability, EnergyAbility
from mods import Mod, ModLocation, ItemObject, Buffs, Proficiencies
from tilemap import ObjectType
from projectiles import ProjectileData, ProjectileFactory


class ShootLaser(FireProjectile):
    _kickback = 0
    _cool_down_time = 500
    _spread = 2
    _projectile_count = 1

    _data = ProjectileData(hits_player=False, damage=100, speed=1000,
                           max_lifetime=1000, image_file=images.LITTLE_LASER,
                           angled_image=True)
    _factory = ProjectileFactory(_data)
    _make_projectile = _factory.build_projectile

    def __init__(self) -> None:
        super().__init__()

    def _fire_effects(self, origin: Vector2) -> None:
        sounds.fire_weapon_sound(ObjectType.LASER_GUN)


class LaserMod(Mod):
    loc = ModLocation.ARMS
    energy_required = 10.0

    def __init__(self, buffs: List[Buffs] = None,
                 profs: List[Proficiencies] = None) -> None:
        super().__init__(buffs, profs)
        self._ability = EnergyAbility(ShootLaser(), self.energy_required)

    @property
    def ability(self) -> Ability:
        return self._ability

    @property
    def expended(self) -> bool:
        return False

    @property
    def description(self) -> str:
        return 'Laser gun'

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

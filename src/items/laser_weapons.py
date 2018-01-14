from pygame.math import Vector2
from pygame.surface import Surface

import images
import sounds
from abilities import ProjectileAbilityData
from data.input_output import load_projectile_data
from mods import ModLocation, ItemObject, ModData, Mod
from tilemap import ObjectType


def laser_pew_sound(origin: Vector2) -> None:
    sounds.fire_weapon_sound(ObjectType.LASER_GUN)


class LaserGun(ItemObject):
    gun_size = (30, 16)

    def __init__(self, pos: Vector2) -> None:
        self._check_class_initialized()

        projectile_data = load_projectile_data('laser')
        ability_data = ProjectileAbilityData(500,
                                             projectile_data=projectile_data,
                                             projectile_count=1,
                                             kickback=0, spread=2,
                                             fire_effects=[laser_pew_sound],
                                             energy_required=10)

        mod_data = ModData(ModLocation.ARMS, ability_data,
                           images.LASER_BOLT, images.LASER_GUN, 'laser gun')
        mod = Mod(mod_data)

        super().__init__(mod, pos)

    @property
    def image(self) -> Surface:
        return images.get_image(images.LASER_GUN)

from pygame.math import Vector2
from pygame.surface import Surface

import images
import sounds

from data.abilities_io import load_ability_data

from mods import ModLocation, ItemObject, ModData, Mod
from tilemap import ObjectType


def laser_pew_sound(origin: Vector2) -> None:
    sounds.fire_weapon_sound(ObjectType.LASER_GUN)


class LaserGun(ItemObject):
    gun_size = (30, 16)

    def __init__(self, pos: Vector2) -> None:
        self._check_class_initialized()

        ability_data = load_ability_data('laser')

        mod_data = ModData(ModLocation.ARMS, ability_data,
                           images.LASER_BOLT, images.LASER_GUN, 'laser gun')
        mod = Mod(mod_data)

        super().__init__(mod, pos)

    @property
    def image(self) -> Surface:
        return images.get_image(images.LASER_GUN)

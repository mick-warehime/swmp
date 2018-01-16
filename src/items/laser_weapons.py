from pygame.math import Vector2
from pygame.surface import Surface

import images

from data.mods_io import load_mod_data

from mods import ItemObject, Mod


class LaserGun(ItemObject):
    gun_size = (30, 16)

    def __init__(self, pos: Vector2) -> None:
        self._check_class_initialized()

        mod = Mod(load_mod_data('laser gun'))

        super().__init__(mod, pos)

    @property
    def image(self) -> Surface:
        return images.get_image(images.LASER_GUN)

from typing import List

from pygame import transform

from pygame.math import Vector2
from pygame.surface import Surface

import images
import sounds
from abilities import Ability, EnergyAbility, ProjectileAbilityData, \
    AbilityFactory
from mods import Mod, ModLocation, ItemObject, Buffs, Proficiencies
from tilemap import ObjectType
from projectiles import ProjectileData


def laser_pew_sound(origin: Vector2) -> None:
    sounds.fire_weapon_sound(ObjectType.LASER_GUN)


class LaserMod(Mod):
    loc = ModLocation.ARMS
    energy_required = 10.0

    def __init__(self, buffs: List[Buffs] = None,
                 profs: List[Proficiencies] = None) -> None:
        super().__init__(buffs, profs)

        projectile_data = ProjectileData(hits_player=False, damage=100,
                                         speed=1000,
                                         max_lifetime=1000,
                                         image_file=images.LITTLE_LASER,
                                         angled_image=True)
        ability_data = ProjectileAbilityData(500,
                                             projectile_data=projectile_data,
                                             projectile_count=1,
                                             kickback=0, spread=2,
                                             fire_effects=[laser_pew_sound])

        base_ability = AbilityFactory(ability_data).build()

        self._ability = EnergyAbility(base_ability, self.energy_required)

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

        # projectile_data = ProjectileData(hits_player=False, damage=100,
        #                                  speed=1000,
        #                                  max_lifetime=1000,
        #                                  image_file=images.LITTLE_LASER,
        #                                  angled_image=True)
        # ability_data = ProjectileAbilityData(500,
        #                                      projectile_data=projectile_data,
        #                                      projectile_count=1,
        #                                      kickback=0, spread=2,
        #                                      fire_effects=[laser_pew_sound])
        #
        # base_ability = FireProjectile(ability_data)

        super().__init__(mod, pos)

    @property
    def image(self) -> Surface:
        return self._image

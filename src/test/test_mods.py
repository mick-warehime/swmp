import unittest
from pygame.math import Vector2
import model
from abilities import AbilityData
from mods import Mod, Proficiencies, Buffs, ModData, ModLocation
from items.bullet_weapons import PistolObject
from src.test.pygame_mock import MockTimer, initialize_pygame, \
    initialize_gameobjects

# needs to be here to prevent screen from loading
import src.test.dummy_audio_video


def setUpModule() -> None:
    initialize_pygame()
    initialize_gameobjects(ModTest.groups, ModTest.timer)
    ModTest.ability_data = AbilityData(10)


class ModTest(unittest.TestCase):
    groups = model.Groups()
    timer = MockTimer()
    ability_data = None

    def tearDown(self) -> None:
        self.groups.empty()
        self.timer.reset()

    def test_item_object_bob_motion(self) -> None:
        pistol_item = PistolObject(Vector2(0, 0))
        time_for_sweep = int(pistol_item._bob_period * 10)

        center = pistol_item.rect.center
        original_center_y = center[1]
        original_center_x = center[0]
        min_center_y = center[1]
        max_center_y = center[1]

        for _ in range(time_for_sweep):
            min_center_y = min(min_center_y, center[1])
            max_center_y = max(max_center_y, center[1])
            self.assertEqual(center[1], original_center_x)

        self.assertEqual(original_center_y, min_center_y)
        self.assertEqual(-original_center_y, max_center_y)

    def test_mod_str_output(self) -> None:
        description = 'banana hammock'
        mod_data = ModData(ModLocation.LEGS, self.ability_data,
                           'no_image', 'no_image', description)
        hammock_mod = Mod(mod_data)

        self.assertEqual(hammock_mod.description, description)
        self.assertEqual(str(hammock_mod), description)

        mod_data = ModData(ModLocation.LEGS, self.ability_data,
                           'no_image', 'no_image', description,
                           buffs=[Buffs.DAMAGE],
                           proficiencies=[Proficiencies.STEALTH])
        nice_mod = Mod(mod_data)

        self.assertIn('damage', str(nice_mod))
        self.assertIn('stealth', str(nice_mod))


if __name__ == '__main__':
    unittest.main()

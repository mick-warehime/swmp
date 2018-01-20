import unittest

from abilities import AbilityData
from data.abilities_io import load_ability_data
from data.items_io import load_item_data
from data.mods_io import load_mod_data
from data.projectiles_io import load_projectile_data
from items import ItemData
from mods import ModData, ModLocation
from projectiles import ProjectileData


class InputOutputTest(unittest.TestCase):
    def test_load_projectile_data(self) -> None:
        data = load_projectile_data('bullet')

        expected_data = ProjectileData(False, 75, 1000, 400, "bullet.png")

        self.assertEqual(data, expected_data)

    def test_load_projectile_bad_input(self) -> None:
        bad_name = 'bullett'

        with self.assertRaisesRegex(KeyError, 'Unrecognized'):
            load_projectile_data(bad_name)

    def test_load_regeneration_ability_data(self) -> None:
        data = load_ability_data('basic_heal')
        expected_data = AbilityData(cool_down_time=300,
                                    heal_amount=20,
                                    finite_uses=True,
                                    uses_left=1,
                                    sound_on_use='health_pack.wav')
        self.assertEqual(data, expected_data)

    def test_load_ability_data_bad_name(self) -> None:
        bad_name = 'seoifjosiejf'

        with self.assertRaisesRegex(KeyError, 'not recognized'):
            load_ability_data(bad_name)

    def test_load_projectile_ability(self) -> None:
        data = load_ability_data('pistol')

        expected_data = AbilityData(250, projectile_label='bullet',
                                    kickback=200,
                                    spread=5, muzzle_flash=True,
                                    sound_on_use='pistol.wav')
        self.assertEqual(data, expected_data)

    def test_load_typical_mod(self) -> None:
        mod_data = load_mod_data('pistol')

        expected_data = ModData(
            ModLocation.ARMS.value, 'pistol', 'mod_pistol.png',
            'obj_pistol.png', 'Pistol')
        self.assertEqual(mod_data, expected_data)

    def test_load_typical_item(self) -> None:
        item_data = load_item_data('pistol')

        expected_data = ItemData('pistol', 'obj_pistol.png')
        self.assertEqual(item_data, expected_data)

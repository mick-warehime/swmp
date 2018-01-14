import unittest

from abilities import RegenerationAbilityData, ProjectileAbilityData
from data.abilities_io import load_ability_data
from data.projectiles_io import load_projectile_data
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
        expected_data = RegenerationAbilityData(cool_down_time=300,
                                                heal_amount=20,
                                                finite_uses=True, uses_left=1)
        self.assertEqual(data, expected_data)

    def test_load_ability_data_bad_name(self) -> None:
        bad_name = 'seoifjosiejf'

        with self.assertRaisesRegex(KeyError, 'not recognized'):
            load_ability_data(bad_name)

    def test_load_projectile_ability(self) -> None:
        data = load_ability_data('pistol')

        proj_data = load_projectile_data('bullet')
        expected_data = ProjectileAbilityData(250, proj_data, kickback=200,
                                              spread=5)
        self.assertEqual(data, expected_data)

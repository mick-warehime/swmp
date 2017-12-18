from src.test.pygame_mock import MockTimer
import unittest
import pygame
import model
import humanoid as hmn
import settings
from item_manager import ItemManager
import mod


def _make_player() -> hmn.Player:
    groups = model.Groups()
    timer = MockTimer()
    pos = pygame.math.Vector2(0, 0)
    player = hmn.Player(groups, timer, pos)
    player.set_weapon('pistol')
    return player

def _make_item(label: str) -> model.Item:
    pos = (0, 0)
    groups = model.Groups()
    return ItemManager.item(groups, pos, label)


class ModTest(unittest.TestCase):
    def test_add_items(self) -> None:
        player = _make_player()
        hp = _make_item(settings.HEALTHPACK_ITEM)

        self.assertEqual(len(player.backpack), 0)

        for i in range(player.backpack_size):
            player.add_item_to_backpack(hp)
            self.assertEqual(len(player.backpack), i + 1)

        self.assertTrue(player.backpack_full())

    def test_use_health_pack(self) -> None:
        player = _make_player()
        hp = _make_item(settings.HEALTHPACK_ITEM)

        self.assertEqual(len(player.backpack), 0)

        player.add_item_to_backpack(hp)

        # health is full
        self.assertFalse(player.damaged)

        hp.use(player)

        # health pack doesn't work if health is full
        self.assertFalse(player.damaged)
        self.assertEqual(len(player.backpack), 1)

        player.increment_health(-settings.HEALTH_PACK_AMOUNT)
        self.assertTrue(player.damaged)
        hp.use(player)

        # health pack fills health back up and is gone from backpack
        self.assertFalse(player.damaged)
        self.assertEqual(len(player.backpack), 0)

        player.add_item_to_backpack(hp)
        player.increment_health(-1)

        hp.use(player)

        # health pack doesn't fill you over max health
        self.assertEqual(player.health, settings.PLAYER_HEALTH)
        self.assertEqual(len(player.backpack), 0)

    def test_add_mod(self) -> None:
        player = _make_player()
        shotgun = _make_item(settings.SHOTGUN_MOD)

        player.add_item_to_backpack(shotgun)

        # nothing installed at arms location -> install shotgun
        self.assertEqual(len(player.backpack), 0)
        arm_mod = player.active_mods[mod.ModLocation.ARMS]
        self.assertEqual(arm_mod, shotgun)

        # adding a second arm mod goes into the backpack
        pistol = _make_item(settings.PISTOL_MOD)

        player.add_item_to_backpack(pistol)
        self.assertEqual(len(player.backpack), 1)
        arm_mod = player.active_mods[mod.ModLocation.ARMS]
        self.assertEqual(arm_mod, shotgun)
        self.assertIn(pistol, player.backpack)

        # make sure we can swap the pistol with the shotgun
        pistol.use(player)
        self.assertEqual(len(player.backpack), 1)
        arm_mod = player.active_mods[mod.ModLocation.ARMS]
        self.assertEqual(arm_mod, pistol)
        self.assertIn(shotgun, player.backpack)


if __name__ == '__main__':
    unittest.main()

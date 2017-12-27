from typing import Union
from pygame.math import Vector2
import pygame
import humanoids as hmn
import mods
from items.item_manager import ItemManager
from dungeon_controller import DungeonController


def make_player() -> hmn.Player:
    pos = pygame.math.Vector2(0, 0)
    player = hmn.Player(pos)
    return player


def make_mob(player: Union[hmn.Player, None] = None) -> hmn.Mob:
    if player is None:
        player = make_player()
    pos = player.pos + pygame.math.Vector2(100, 0)
    return hmn.Mob(pos, player, is_quest=False)


def make_item(label: str) -> mods.ItemObject:
    pos = Vector2(0, 0)
    return ItemManager.item(pos, label)


def make_dungeon_controller() -> DungeonController:
    level = 'test_level.tmx'
    blank_screen = pygame.Surface((800, 600))
    return DungeonController(blank_screen, level)

from typing import Union

import pygame
from pygame.math import Vector2

import creatures.mobs
import creatures.players
import mods
import controller
from dungeon_controller import DungeonController
from items.item_manager import ItemManager


def make_player() -> creatures.players.Player:
    pos = pygame.math.Vector2(0, 0)
    player = creatures.players.Player(pos)
    return player


def make_mob(player: Union[creatures.players.Player, None] = None) -> creatures.mobs.Mob:
    if player is None:
        player = make_player()
    pos = player.pos + pygame.math.Vector2(100, 0)
    return creatures.mobs.Mob(pos, player, conflict_group=None)


def make_item(label: str) -> mods.ItemObject:
    pos = Vector2(0, 0)
    return ItemManager.item(pos, label)


def make_dungeon_controller() -> DungeonController:
    blank_screen = pygame.Surface((800, 600))
    controller.initialize_controller(blank_screen, None)
    level = 'test_level.tmx'
    return DungeonController(level)


class TiledmapObject(object):
    def __init__(self,
                 object_name: str,
                 conflict_name: str = None) -> None:
        self.name = object_name
        self.x = 0
        self.y = 0
        self.width = 10
        self.height = 10
        if conflict_name is not None:
            self.conflict = conflict_name

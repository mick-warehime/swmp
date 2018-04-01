from typing import Union

import pygame
from pygame.math import Vector2

import creatures.enemies
import creatures.players
import items
from controllers.base import initialize_controller
from controllers.dungeon_controller import DungeonController, Dungeon
from controllers.turnbased_controller import TurnBasedDungeon
from controllers.turnbased_controller import TurnBasedController
from data.constructors import build_map_object


def make_player() -> creatures.players.Player:
    pos = pygame.math.Vector2(0, 0)
    player = creatures.players.Player(pos)
    return player


def make_zombie(player: Union[
    creatures.players.Player, None] = None) -> creatures.enemies.Enemy:
    if player is None:
        player = make_player()
    pos = player.pos + pygame.math.Vector2(100, 0)
    return build_map_object('zombie', pos, player)


def make_item(label: str) -> items.ItemObject:
    pos = Vector2(0, 0)
    return build_map_object(label, pos)


def make_dungeon_controller() -> DungeonController:
    initialize_controller(None)

    dungeon = Dungeon('test_level.tmx')

    return DungeonController(dungeon, [])


def make_turnbased_controller() -> DungeonController:
    initialize_controller(None)

    dungeon = TurnBasedDungeon('test_turnbased.tmx')

    return TurnBasedController(dungeon, [])

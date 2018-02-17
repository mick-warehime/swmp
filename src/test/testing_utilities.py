from typing import Union

import os
import pygame
from pygame.math import Vector2

import controller
import creatures.enemies
import creatures.players
import items
from data.constructors import build_map_object
from dungeon_controller import DungeonController, Dungeon


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
    blank_screen = pygame.Surface((800, 600))
    controller.initialize_controller(blank_screen, None)

    dungeon = Dungeon('test_level.tmx')

    return DungeonController(dungeon)

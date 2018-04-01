from random import random
from typing import Dict, List, Tuple, Set

import pygame as pg
from pygame.sprite import spritecollide, groupcollide

import controllers.base
import model
import mods
import tilemap
from controllers import keyboards
from creatures.enemies import Enemy
from creatures.humanoids import collide_hit_rect_with_rect, HumanoidData
from creatures.players import Player
from data import constructors
from items import ItemObject
from projectiles import Projectile
from quests.resolutions import Resolution, RequiresTeleport
from view import turnbased_view, sounds
from party import Party
from party_member import PartyMember

class TurnBasedDungeon(model.GroupsAccess):
    """Stores and updates GameObjects in a dungeon map."""

    def __init__(self, map_file: str) -> None:

        # init_map
        self.map = tilemap.TiledMap(map_file)
        self.labeled_sprites: Dict[str, Set[model.GameObject]] = {}
        self._init_map_objects()

    def _init_map_objects(self) -> None:

        # initialize the player on the map before anything else
        for obj in self.map.objects:
            if obj.type == tilemap.ObjectType.PLAYER:
                self.player = Player(obj.center)

        assert self.player is not None, 'no player found in map'

        builder = constructors.build_map_object
        for obj in self.map.objects:

            if obj.type == tilemap.ObjectType.PLAYER:
                game_obj = self.player
            else:
                dims = (obj.width, obj.height)
                game_obj = builder(obj.type, obj.center, self.player, dims)
            # TODO(dvirk): Ideally this should be handled outside the scope of
            # Dungeon. Perhaps this whole method should be handled outside.
            for label in obj.labels:
                if label not in self.labeled_sprites:
                    self.labeled_sprites[label] = {game_obj}
                else:
                    self.labeled_sprites[label].add(game_obj)

    def update(self) -> None:
        self.groups.all_sprites.update()


class TurnBasedController(controllers.base.Controller):
    """Manages interactions between a Dungeon, DungeonView, Resolutions, and
     user.
     """

    def __init__(self, dungeon: TurnBasedDungeon,
                 resolutions: List[Resolution]) -> None:
        super().__init__()

        self._dungeon = dungeon

        self._view = turnbased_view.TurnBasedView()
        self._view.set_camera_range(self._dungeon.map.width,
                                    self._dungeon.map.height)

        self._teleport_resolutions: List[RequiresTeleport] = None
        self._teleport_resolutions = [res for res in resolutions if
                                      isinstance(res, RequiresTeleport)]

        self._init_controls()

        self._party = Party()
        for i in range(1, 4):
            member = PartyMember(pg.math.Vector2(50, 400 + i * 32))
            self._party.add_member(member)

    def set_player_data(self, data: HumanoidData) -> None:
        self._dungeon.player.data = data

    def draw(self) -> None:
        self._view.draw(self._party, self._dungeon.map)

        pg.display.flip()

    def update(self) -> None:
        self.keyboard.handle_input()
        self._dungeon.update()

    def _init_controls(self) -> None:
        pass

    # mouse coordinates are relative to the camera
    # most other coordinates are relative to the map
    def _abs_mouse_pos(self) -> Tuple[int, int]:
        mouse_pos = pg.mouse.get_pos()
        camera_pos = self._view.camera.rect
        abs_mouse_x = mouse_pos[0] - camera_pos[0]
        abs_mouse_y = mouse_pos[1] - camera_pos[1]
        return abs_mouse_x, abs_mouse_y

    # Ensures that gameobjects are removed from Groups once the controller
    # is no longer used.
    def __del__(self) -> None:
        self._dungeon.groups.empty()
        del self

from typing import Dict, List, Tuple, Set
import pygame as pg
import controllers.base
import model

import tilemap

from creatures.humanoids import HumanoidData
from creatures.players import Player
from data import constructors
from quests.resolutions import Resolution, RequiresTeleport
from view import turnbased_view
from creatures.party import example_party


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
        self._party = example_party()

        # roll initiative
        self._party.prepare_for_combat()

        self._view = turnbased_view.TurnBasedView(self._party)
        self._view.set_camera_range(self._dungeon.map.width,
                                    self._dungeon.map.height)

        self._teleport_resolutions: List[RequiresTeleport] = None
        self._teleport_resolutions = [res for res in resolutions if
                                      isinstance(res, RequiresTeleport)]

        self._init_controls()

    def set_player_data(self, data: HumanoidData) -> None:
        self._dungeon.player.data = data

    def draw(self) -> None:
        self._view.draw(self._dungeon.map)

        pg.display.flip()

    def update(self) -> None:

        # needs a wait until moved loop
        # wait until choose attack move
        # wait until clicks end turn move
        # needs a end turn button

        if self.keyboard.mouse_just_clicked:
            self._handle_mouse()
            self.keyboard.handle_input(['none allowed'])
        else:
            self.keyboard.handle_input()

        self._dungeon.update()

    def _handle_mouse(self) -> None:
        self._view._try_move(self._abs_mouse_pos())

    def _init_controls(self) -> None:
        self.keyboard.bind_on_press(pg.K_h, self._view.toggle_debug)

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

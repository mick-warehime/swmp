from enum import unique, Enum
from os import path
from typing import Any, List, Set

import pygame as pg
import pytmx

from data.input_output import is_npc_type, is_item_type

CONFLICT = 'conflict'
NOT_CONFLICT = 'not_conflict'


@unique
class ObjectType(Enum):
    PLAYER = 'player'
    ZOMBIE = 'zombie'
    QUEST_ZOMBIE = 'quest_zombie'
    WALL = 'wall'
    PISTOL = 'pistol'
    HEALTHPACK = 'healthpack'
    ROCK = 'rock'
    SHOTGUN = 'shotgun'
    CONFLICT = 'conflict'
    WAYPOINT = 'waypoint'
    LASER_GUN = 'laser'
    BATTERY = 'battery'
    TURRET = 'turret'


class MapObject(object):
    '''simple wrapper class for objects in the tiled map'''

    def __init__(self, tile_object: Any) -> None:
        self.x = tile_object.x
        self.y = tile_object.y
        center_x = tile_object.x + tile_object.width / 2
        center_y = tile_object.y + tile_object.height / 2
        self.center = pg.math.Vector2(center_x, center_y)
        self.width = tile_object.width
        self.height = tile_object.height
        self.type = self._parse_type(tile_object.name)
        # self.conflict = self._parse_conflict(tile_object)
        if hasattr(tile_object, 'labels'):
            labels_str = getattr(tile_object, 'labels')
            self.labels = set(labels_str.split(' '))
        else:
            self.labels: Set[str] = None

    # def _parse_conflict(self, tile_object: Any) -> str:
    #     return getattr(tile_object, CONFLICT, NOT_CONFLICT)

    def _parse_type(self, type_name: str) -> ObjectType:
        return type_name
        # for obj_type in ObjectType:
        #     if type_name == obj_type:
        #         return obj_type
        #
        # raise ValueError('invalid object type %s @ %d',
        #                  type_name,
        #                  self.center)


class TiledMap:
    def __init__(self, filename: str) -> None:
        game_folder = path.dirname(__file__)
        map_folder = path.join(game_folder, 'maps')
        full_path = path.join(map_folder, filename)
        tm = pytmx.load_pygame(full_path, pixelalpha=True)

        self.width = tm.width * tm.tilewidth
        self.height = tm.height * tm.tileheight
        self.tmxdata = tm

        self._validate_tmxdata()
        self._format_tileobject_names()
        self.img = self.make_map_img()
        self.rect = self.img.get_rect()
        self.objects: List[MapObject] = \
            list(map(MapObject, self.tmxdata.objects))

    def _format_tileobject_names(self) -> None:
        for tile_object in self.tmxdata.objects:
            try:
                # Eventually we will not need the ObjectType Enum
                tile_object.name = ObjectType(tile_object.name)
            except ValueError:
                pass

    def _validate_tmxdata(self) -> None:
        expected_names = {tile.value for tile in ObjectType}
        names = {obj.name for obj in self.tmxdata.objects}
        bad_names = names - expected_names
        # TODO(dvirk): make is_gameobject_type function
        bad_names = {nm for nm in bad_names if not is_npc_type(nm)}
        bad_names = {nm for nm in bad_names if not is_item_type(nm)}
        if bad_names:
            raise ValueError(
                'Tile names %s not recognized.' % (list(bad_names)))

    def render(self, surface: pg.Surface) -> None:
        ti = self.tmxdata.get_tile_image_by_gid
        for layer in self.tmxdata.visible_layers:
            if isinstance(layer, pytmx.TiledTileLayer):
                for x, y, gid, in layer:
                    tile = ti(gid)
                    if tile:
                        surface.blit(tile, (x * self.tmxdata.tilewidth,
                                            y * self.tmxdata.tileheight))

    def make_map_img(self) -> pg.Surface:
        temp_surface = pg.Surface((self.width, self.height))
        self.render(temp_surface)
        return temp_surface

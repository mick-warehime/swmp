from enum import unique, Enum
import pygame as pg
import pytmx
from typing import Any, List
from settings import WIDTH, HEIGHT
from os import path

CONFLICT = 'conflict'
NOT_CONFLICT = 'not_conflict'


@unique
class ObjectType(Enum):
    PLAYER = 'player'
    ZOMBIE = 'zombie'
    WALL = 'wall'
    PISTOL = 'pistol'
    HEALTHPACK = 'healthpack'
    ROCK = 'rock'
    SHOTGUN = 'shotgun'
    CONFLICT = 'conflict'
    WAYPOINT = 'waypoint'
    LASER_GUN = 'laser'
    BATTERY = 'battery'


ITEMS = (ObjectType.HEALTHPACK, ObjectType.SHOTGUN, ObjectType.PISTOL,
         ObjectType.ROCK, ObjectType.LASER_GUN, ObjectType.BATTERY)


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
        self.conflict = self._parse_conflict(tile_object)

    def _parse_conflict(self, tile_object: Any) -> str:
        return getattr(tile_object, CONFLICT, NOT_CONFLICT)

    def _parse_type(self, type_name: str) -> ObjectType:
        for obj_type in ObjectType:
            if type_name == obj_type:
                return obj_type

        raise ValueError('invalid object type %s @ %d',
                         type_name,
                         self.center)


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
            tile_object.name = ObjectType(tile_object.name)

    def _validate_tmxdata(self) -> None:
        expected_names = {tile.value for tile in ObjectType}
        names = {obj.name for obj in self.tmxdata.objects}
        bad_names = names - expected_names
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


class Camera:
    def __init__(self, width: int, height: int) -> None:
        self.rect = pg.Rect(0, 0, width, height)
        self.width = width
        self.height = height

    def apply(self, sprite: pg.sprite.Sprite) -> pg.Rect:
        return sprite.rect.move(self.rect.topleft)

    def apply_rect(self, rect: pg.Rect) -> pg.Rect:
        return rect.move(self.rect.topleft)

    def update(self, target: pg.sprite.Sprite) -> None:
        x = -target.rect.centerx + int(WIDTH / 2)
        y = -target.rect.centery + int(HEIGHT / 2)

        # limit scrolling to map size
        x = min(0, x)  # left
        y = min(0, y)  # top
        x = max(-(self.width - WIDTH), x)  # right
        y = max(-(self.height - HEIGHT), y)  # bottom
        self.rect = pg.Rect(x, y, self.width, self.height)

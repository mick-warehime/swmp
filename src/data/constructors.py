from typing import Union, Any, Tuple

from pygame.math import Vector2
from pygame.sprite import Sprite

from creatures.enemies import EnemyData, Enemy
from data.input_output import load_item_data_kwargs, load_npc_data_kwargs, \
    is_npc_type, is_item_type
from items import ItemFromData, ItemData
from model import GameObject, Zone, Obstacle
from tilemap import ObjectType
from waypoints import Waypoint


def build_map_object(label: Union[ObjectType, str], pos: Vector2,
                     player: Any = None,
                     dimensions: Tuple[int, int] = None) -> Sprite:
    label_str = label if isinstance(label, str) else label.value
    if is_npc_type(label_str):
        data = EnemyData(**load_npc_data_kwargs(label_str))
        return Enemy(pos, player, data)
    elif is_item_type(label_str):
        data = ItemData(**load_item_data_kwargs(label_str))
        return ItemFromData(data, pos)
    elif label == ObjectType.ZONE:
        assert dimensions is not None
        top_left = Vector2(pos[0] - dimensions[0] / 2,
                           pos[1] - dimensions[1] / 2)
        return Zone(top_left, dimensions[0], dimensions[1])
    elif label == ObjectType.WALL:
        assert dimensions is not None
        top_left = Vector2(pos[0] - dimensions[0] / 2,
                           pos[1] - dimensions[1] / 2)
        return Obstacle(top_left, dimensions[0], dimensions[1])

    else:
        if label != ObjectType.WAYPOINT:
            raise ValueError('Unrecognized object of type %s.' % (label,))
        return Waypoint(pos, player)

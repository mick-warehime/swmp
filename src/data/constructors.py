from typing import Union, Any

from pygame.math import Vector2
from pygame.sprite import Group

from creatures.enemies import EnemyData, Enemy
from data.input_output import load_item_data_kwargs, load_npc_data_kwargs, \
    is_npc_type, is_item_type
from items import ItemFromData, ItemData
from model import GameObject
from tilemap import ObjectType
from waypoints import Waypoint


def build_map_object(label: Union[ObjectType, str], pos: Vector2,
                     player: Any = None) -> GameObject:
    label_str = label if isinstance(label, str) else label.value
    if is_npc_type(label_str):
        data = EnemyData(**load_npc_data_kwargs(label_str))
        # if conflict_group is not None:
        #     data = data.add_quest_group(conflict_group)
        return Enemy(pos, player, data)
    elif is_item_type(label_str):
        data = ItemData(**load_item_data_kwargs(label_str))
        return ItemFromData(data, pos)
    else:
        if label != ObjectType.WAYPOINT:
            raise ValueError('Unrecognized object of type %s.' % (label,))
        return Waypoint(pos, player)

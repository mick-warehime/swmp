from typing import List, Dict

from controllers.dungeon_controller import Dungeon, DungeonController
from quests.resolutions import resolution_from_data
from quests.scenes.interface import ControllerAndResolutions, Scene


class DungeonScene(Scene):
    def __init__(self, map_file: str, resolution_datas: List[Dict]) -> None:
        self._map_file = map_file

        self._resolution_datas = resolution_datas

    def make_controller_and_resolutions(self) -> ControllerAndResolutions:
        dungeon = Dungeon(self._map_file)
        sprite_labels = dungeon.labeled_sprites

        resolutions = [resolution_from_data(data) for data in
                       self._resolution_datas]

        for resolution in resolutions:
            resolution.load_sprite_data(sprite_labels)

        return DungeonController(dungeon), resolutions

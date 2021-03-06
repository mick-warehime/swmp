from typing import List, Dict
from controllers.turnbased_controller import TurnBasedDungeon
from controllers.turnbased_controller import TurnBasedController
from quests.resolutions import resolution_from_data
from quests.scenes.interface import ControllerAndResolutions, Scene


class TurnBasedScene(Scene):
    def __init__(self, map_file: str, resolution_datas: List[Dict]) -> None:
        self._map_file = map_file

        self._resolution_datas = resolution_datas

    def make_controller_and_resolutions(self) -> ControllerAndResolutions:
        dungeon = TurnBasedDungeon(self._map_file)
        sprite_labels = dungeon.labeled_sprites

        resolutions = [resolution_from_data(data) for data in
                       self._resolution_datas]

        for resolution in resolutions:
            resolution.load_sprite_data(sprite_labels)

        ctrl = TurnBasedController(dungeon, resolutions)
        return ctrl, resolutions

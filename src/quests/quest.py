from typing import Dict, Union, Sequence

import networkx

from creatures import players
from creatures.humanoids import HumanoidData, Status, Inventory
from quests.resolutions import Resolution
from quests.scenes import make_scene, Scene, SceneType


class Quest(object):
    """Handles transitions between different Controllers (scenes)"""

    def __init__(self, quest_data: Dict[str, Dict]) -> None:

        self._player_data: HumanoidData = None
        self._scene_graph = self._make_quest_graph(quest_data)

        self._root_scene = self._get_scene('root')
        self._set_current_scene(self._root_scene)

    def update_and_draw(self) -> None:
        self._current_ctrl.update()
        self._current_ctrl.draw()

        resolution = self._resolved_resolution()
        if resolution is not None:
            next_scene = self._resolutions_to_scenes[resolution]
            self._set_current_scene(next_scene)

    def _get_scene(self, label: str) -> Scene:
        nodes = [node for node, info in self._scene_graph.nodes.data() if info[
            'label'] == label]

        if len(nodes) != 1:
            raise KeyError('Expected exactly one scene to be labeled `{}`, but'
                           ' instead got {}'.format(label, len(nodes)))
        return nodes[0]

    def _make_quest_graph(
            self, quest_data: Dict[str, Dict]) -> networkx.MultiDiGraph:
        graph = networkx.MultiDiGraph()
        label_scene_map = {}
        for label, scene_data in quest_data.items():
            scene = make_scene(scene_data)
            graph.add_node(scene, label=label)
            label_scene_map[label] = scene

        self._add_edges_to_graph(graph, quest_data, label_scene_map)
        return graph

    def _add_edges_to_graph(
            self, graph: networkx.MultiDiGraph, quest_data: Dict[str, Dict],
            label_scene_map: Dict[str, Scene]) -> None:

        for label, scene in label_scene_map.items():
            scene_data = quest_data[label]

            scene_type = SceneType(scene_data['type'])
            if scene_type == SceneType.DECISION:
                for index, choice in enumerate(scene_data['choices']):
                    assert len(choice.values()) == 1
                    next_scene_label = list(choice.values())[0]
                    next_scene = label_scene_map[next_scene_label]
                    graph.add_edge(scene, next_scene, key=index)
            elif scene_type == SceneType.TRANSITION:
                next_scene = label_scene_map[scene_data['next scene']]
                graph.add_edge(scene, next_scene, key=0)
            else:
                assert scene_type == SceneType.DUNGEON
                for index, resolution in enumerate(scene_data['resolutions']):
                    assert len(resolution.values()) == 1
                    res_data = list(resolution.values())[0]
                    next_scene_label = res_data['next scene']
                    next_scene = label_scene_map[next_scene_label]
                    graph.add_edge(scene, next_scene, key=index)

    def _set_current_scene(self, scene: Scene) -> None:
        self._current_scene = scene
        ctrl, resltns = self._current_scene.make_controller_and_resolutions()
        self._current_ctrl = ctrl

        if self._current_scene is self._root_scene:
            self._player_data = HumanoidData(Status(players.PLAYER_HEALTH),
                                             Inventory())
        self._current_ctrl.set_player_data(self._player_data)

        resols = self._resolution_to_next_scene_map(scene, resltns)
        self._resolutions_to_scenes = resols

    def _resolution_to_next_scene_map(
            self, current_scene: Scene,
            resolutions: Sequence[Resolution]) -> Dict[Resolution, Scene]:
        """ The Scene object outputs resolutions in a specific order. We match
        that order to the key assigned to each edge, which tells us what scene
        each resolution points to."""

        # Output of out_edges is a list of tuples of the form
        # (source : Scene, sink : Scene, key : int)
        # The key is the resolution index, as stored in resolutions.
        next_scenes = self._scene_graph.out_edges(current_scene, keys=True)
        next_scenes = sorted(next_scenes, key=lambda x: x[2])
        resols = {res: scene_tup[1] for res, scene_tup in
                  zip(resolutions, next_scenes)}
        return resols

    def _resolved_resolution(self) -> Union[Resolution, None]:
        resolved = [res for res in self._resolutions_to_scenes if
                    res.is_resolved]

        if len(resolved) not in (0, 1):
            raise Warning('More than one resolved resolutions: {}. '
                          'Choosing first in list.'.format(resolved))

        if resolved:
            return resolved[0]
        else:
            return None

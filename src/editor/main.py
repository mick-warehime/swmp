"""Editor for creating new quests."""
import tkinter
from collections import OrderedDict
from tkinter import filedialog
from typing import List, Iterable, Dict, Any

import math

from data.input_output import load_quest_data
from editor.util import assert_yaml_filename, draw_circle, \
    close_window_after_call
from quests.scenes.builder import SceneType, next_scene_labels

_scene_type_letter = {SceneType.DECISION: 'D', SceneType.DUNGEON: 'C',
                      SceneType.SKILL_CHECK: 'S', SceneType.TRANSITION: 'T'}


def _start_window() -> tkinter.Tk:
    root = tkinter.Tk()
    root.resizable(width=False, height=False)
    root.title('Quest editor')
    return root


def _quest_editor_window(filename: str, full_path=True) -> tkinter.Tk:
    assert_yaml_filename(filename)

    root = tkinter.Tk()
    root.title(filename)

    node_spacing_x = 140
    min_spacing_y = 250
    base_offset_x = 50

    canvas = tkinter.Canvas(root, width=1024, height=736)
    canvas.pack()

    quest_data = load_quest_data(filename, full_path)

    # root_data = quest_data['root']
    # scene_type = SceneType(root_data['type'])

    current_scenes = ['root']
    quest_levels = [{'root'}]
    max_num_rows = 1

    while current_scenes:

        all_next_scenes = set()
        for scene_label in current_scenes:
            all_next_scenes |= set(next_scene_labels(quest_data[scene_label]))
        all_next_scenes -= {'root'}
        max_num_rows = max(max_num_rows, len(all_next_scenes))

        quest_levels.append(all_next_scenes)
        current_scenes = all_next_scenes

    column_length = (max_num_rows - 1) * min_spacing_y

    nodes = []
    last_level_nodes = []
    for col, level in enumerate(quest_levels):

        scenes_in_level = list(level)

        y_spacing = column_length / (len(scenes_in_level) + 1)
        y_offset = y_spacing

        pos_x = base_offset_x + col * node_spacing_x

        current_level_nodes = []
        for row, scene_label in enumerate(scenes_in_level):
            data = quest_data[scene_label]
            node = QuestNode(scene_label, data, pos_x, y_offset + row * \
                             y_spacing, canvas)
            current_level_nodes.append(node)
            nodes.append(node)

        for last_node in last_level_nodes:
            children_labels = next_scene_labels(quest_data[last_node.label])
            neighbors = [node for node in current_level_nodes
                         if node.label in children_labels]
            last_node.add_children(neighbors)

        last_level_nodes = current_level_nodes

    return root


class QuestNode(object):
    def __init__(self, label: str, data: Dict[str, Any], pos_x, pos_y,
                 canvas: tkinter.Canvas, color=None, radius=15):
        self._image = draw_circle(pos_x, pos_y, radius, canvas, fill=color)
        self.label = label
        self._data = data
        self.radius = radius
        self._child_edges = {}
        self.x = pos_x
        self.y = pos_y
        self._canvas: tkinter.Canvas = canvas

        self._texts = []

        self._texts.append(
            canvas.create_text(pos_x, pos_y + radius * 2, text=label))
        letter = _scene_type_letter[SceneType(self._data['type'])]
        self._texts.append(
            canvas.create_text(pos_x, pos_y, text=letter)
        )

    def add_children(self, children: Iterable['QuestNode']) -> None:
        for child in children:
            self.add_child(child)

    def add_child(self, node: 'QuestNode'):
        if node not in self._child_edges.keys():
            dx = (node.x - self.x)
            dy = (node.y - self.y)
            line_length = math.sqrt(dx ** 2 + dy ** 2)
            assert line_length > max(node.radius, self.radius)

            scaling_initial = self.radius / line_length
            start_x = self.x + scaling_initial * dx
            start_y = self.y + scaling_initial * dy

            scaling_final = (line_length - node.radius) / line_length

            final_x = self.x + scaling_final * dx
            final_y = self.y + scaling_final * dy

            line = self._canvas.create_line(start_x, start_y, final_x, final_y,
                                            arrow=tkinter.LAST)
            self._child_edges[node] = line

    def __str__(self):
        child_labels = [node.label for node in self._child_edges.keys()]
        return "Node({}), children: {}".format(self.label, child_labels)


def _new_quest() -> None:
    filename = filedialog.asksaveasfilename()
    if filename[-4:] != '.yml':
        filename += '.yml'
    _quest_editor_window(filename)


def _open_quest() -> None:
    filename = filedialog.askopenfilename()

    _quest_editor_window(filename)


def main() -> None:
    root = _start_window()

    new_fun = close_window_after_call(_new_quest, root)
    new_button = tkinter.Button(root, text="New Quest", command=new_fun)
    new_button.pack(pady=10)

    open_fun = close_window_after_call(_open_quest, root)
    open_button = tkinter.Button(root, text="Open Quest", command=open_fun)
    open_button.pack(pady=10)

    quit_button = tkinter.Button(root, text="Quit", command=root.quit)
    quit_button.pack(pady=10)

    # _quest_editor_window('zombie_quest.yml', full_path=False)

    tkinter.mainloop()


if __name__ == '__main__':
    main()

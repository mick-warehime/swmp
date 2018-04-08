"""Editor for creating new quests."""
import tkinter
from tkinter import filedialog
from typing import Callable

from data.input_output import load_quest_data
from editor import util
from editor.nodes import node_registry, QuestNode
from editor.util import assert_yaml_filename, CanvasAccess
from quests.scenes.builder import next_scene_labels

"""TODO:
- Enable scrolling within the graph window.
- Node editor (just display standard fields for each scene type).
- Saving updated data.
- Creation of new nodes (this will be done using currently existing nodes?)
"""


def _quest_editor_window(filename: str, full_path=True) -> tkinter.Tk:
    assert_yaml_filename(filename)

    root = util.new_window(filename)

    node_spacing_x = 140
    min_spacing_y = 250
    base_offset_x = 50

    canvas = tkinter.Canvas(root, width=1024, height=736)
    canvas.pack()
    canvas.bind('<Button-1>', apply_for_canvas(on_mouse1_click, canvas))
    CanvasAccess.set_canvas(canvas)

    quest_data = load_quest_data(filename, full_path)

    quest_levels = _quest_levels(quest_data)
    max_num_rows = max(len(level) for level in quest_levels)

    column_length = (max_num_rows - 1) * min_spacing_y

    _build_nodes(base_offset_x, column_length, node_spacing_x, quest_data,
                 quest_levels)

    return root


def _build_nodes(base_offset_x, column_length, node_spacing_x, quest_data,
                 quest_levels):
    nodes = []
    prev_level_nodes = []
    for col, level in enumerate(quest_levels):

        scenes_in_level = list(level)

        y_spacing = column_length / (len(scenes_in_level) + 1)
        y_offset = y_spacing

        pos_x = base_offset_x + col * node_spacing_x

        current_level_nodes = []
        for row, scene_label in enumerate(scenes_in_level):
            data = quest_data[scene_label]
            node = QuestNode(scene_label, data, pos_x, y_offset + row * \
                             y_spacing)
            current_level_nodes.append(node)
            nodes.append(node)

        for prev_node in prev_level_nodes:
            children_labels = next_scene_labels(quest_data[prev_node.label])
            neighbors = [node for node in current_level_nodes
                         if node.label in children_labels]
            prev_node.add_children(neighbors)

        prev_level_nodes = current_level_nodes


def _quest_levels(quest_data):
    current_scenes = ['root']
    quest_levels = [{'root'}]
    while current_scenes:

        all_next_scenes = set()
        for scene_label in current_scenes:
            all_next_scenes |= set(next_scene_labels(quest_data[scene_label]))
        all_next_scenes -= {'root'}

        quest_levels.append(all_next_scenes)
        current_scenes = all_next_scenes
    return quest_levels


def apply_for_canvas(func: Callable, canvas: tkinter.Canvas) -> Callable:
    def wrapper_fun(*args, **kwargs):
        return func(*args, **kwargs, canvas=canvas)

    return wrapper_fun


def on_mouse1_click(event, canvas: tkinter.Canvas = None):
    currently_selected = canvas.gettags('current')
    if any(tag in currently_selected for tag in ('circle', 'type')):
        node_tag = [tag for tag in currently_selected if 'Node' in tag]
        assert len(node_tag) == 1
        node = node_registry[node_tag[0]]
        node.select()


def _new_quest() -> None:
    filename = filedialog.asksaveasfilename()
    if filename[-4:] != '.yml':
        filename += '.yml'
    _quest_editor_window(filename)


def _open_quest() -> None:
    filename = filedialog.askopenfilename()

    _quest_editor_window(filename)


def main() -> None:
    # root = util.new_window('Quest editor', resizable=False)
    #
    # new_fun = util.close_window_after_call(_new_quest, root)
    # new_button = tkinter.Button(root, text="New Quest", command=new_fun)
    # new_button.pack(pady=10)
    #
    # open_fun = util.close_window_after_call(_open_quest, root)
    # open_button = tkinter.Button(root, text="Open Quest", command=open_fun)
    # open_button.pack(pady=10)
    #
    # quit_button = tkinter.Button(root, text="Quit", command=root.quit)
    # quit_button.pack(pady=10)

    _quest_editor_window('zombie_quest.yml', full_path=False)

    tkinter.mainloop()


if __name__ == '__main__':
    main()

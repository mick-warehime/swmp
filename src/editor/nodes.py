import math
import tkinter
from typing import Dict, Any, Iterable

from editor.util import draw_circle, CanvasAccess, \
    canvas_coords_to_master_coords, new_window
from quests.scenes.builder import SceneType

_scene_type_letter = {SceneType.DECISION: 'D', SceneType.DUNGEON: 'C',
                      SceneType.SKILL_CHECK: 'S', SceneType.TRANSITION: 'T'}
node_registry = {}
selected_nodes = set()


class QuestNode(CanvasAccess):
    def __init__(self, label: str, data: Dict[str, Any], pos_x, pos_y,
                 color="", radius=15):
        super().__init__()
        self.label = label

        self._data = data
        self.radius = radius
        self.x = pos_x
        self.y = pos_y
        self._editor: tkinter.Tk = None

        self._child_edges = {}
        self._selected_linewidth = 3
        self._unselected_linewidth = 1
        self._circle = draw_circle(pos_x, pos_y, radius, self.canvas,
                                   fill=color, tags=('circle', self.tag))
        self.deselect()

        self._texts = []

        self._texts.append(
            self.canvas.create_text(pos_x, pos_y + radius * 2, text=label,
                                    tags=('label', self.tag)))
        letter = _scene_type_letter[SceneType(self._data['type'])]
        self._texts.append(
            self.canvas.create_text(pos_x, pos_y, text=letter,
                                    tags=('type', self.tag))
        )

        node_registry[self.tag] = self

    def select(self) -> None:

        if selected_nodes:
            previous_node = selected_nodes.pop()

            previous_node.deselect()
            if self is previous_node:
                return

        selected_nodes.add(self)
        self.canvas.itemconfig(self._circle, width=self._selected_linewidth)

        self._open_editor_window()

    def _open_editor_window(self):
        wx, wy = canvas_coords_to_master_coords(self.canvas, self.x, self.y)
        window_offset_x = self.canvas.master.winfo_x() + 30
        window_offset_y = self.canvas.master.winfo_y() - 30
        dimensions = (300, 200, wx + window_offset_x, wy + window_offset_y)
        self._editor = new_window(str(self), dimensions)

    def deselect(self):
        self.canvas.itemconfig(self._circle, width=self._unselected_linewidth)
        self._close_editor_window()

    def _close_editor_window(self):
        if self._editor:
            self._editor.destroy()
            self._editor = None

    @property
    def tag(self) -> str:
        return 'Node {} ({})'.format(self.label, str(self.__hash__()))

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

            line = self.canvas.create_line(start_x, start_y, final_x, final_y,
                                           arrow=tkinter.LAST, tags=(
                    'edge', self.tag, node.tag))
            self._child_edges[node] = line

    def __str__(self):
        child_labels = [node.label for node in self._child_edges.keys()]
        return "Node({}), children: {}".format(self.label, child_labels)



import math
import tkinter
from typing import Dict, Any, Iterable, Tuple

from editor import editors
from editor.util import draw_circle, CanvasAccess, \
    canvas_coords_to_master_coords
from quests.scenes.builder import SceneType

_scene_type_letter = {SceneType.DECISION: 'D', SceneType.DUNGEON: 'C',
                      SceneType.SKILL_CHECK: 'S', SceneType.TRANSITION: 'T'}
_selectables_registry = {}


class Selectable(object):
    """Denotes a selectable object on a canvas."""
    selected_object: 'Selectable' = None

    def __init__(self):
        _selectables_registry[str(hash(self))] = self

    def _on_select(self):
        raise NotImplementedError

    def _on_deselect(self):
        raise NotImplementedError

    @property
    def tags(self) -> Tuple[str, str]:
        return str(hash(self)), 'selectable'

    def select(self):

        if Selectable.selected_object is not None:
            previous_selected = Selectable.selected_object

            previous_selected.deselect()
            if self is previous_selected:
                return

        Selectable.selected_object = self

        self._on_select()

    def deselect(self):
        self._on_deselect()

    @classmethod
    def from_tags(cls, tags: Tuple[str, ...]) -> 'Selectable':
        id_tags = [tag for tag in tags if tag in _selectables_registry]
        if not id_tags:
            raise KeyError(
                'No id tags recognized in registry, for tags {}'.format(tags))
        return _selectables_registry[id_tags[0]]


class SceneNode(CanvasAccess, Selectable):
    _selected_linewidth = 4
    _unselected_linewidth = 1

    def __init__(self, label: str, data: Dict[str, Any], pos_x, pos_y,
                 color="", radius=15):
        super().__init__()
        Selectable.__init__(self)
        self.label = label

        self._data = data
        self.radius = radius
        self.x = pos_x
        self.y = pos_y
        self._editor: tkinter.Tk = None

        self._child_edges = {}

        self._circle = draw_circle(pos_x, pos_y, radius, self.canvas,
                                   fill=color, tags=('circle',) + self.tags)

        self._texts = []

        self._texts.append(
            self.canvas.create_text(pos_x, pos_y + radius * 2, text=label,
                                    tags=('label',) + self.tags))
        letter = _scene_type_letter[SceneType(self._data['type'])]
        self._texts.append(
            self.canvas.create_text(pos_x, pos_y, text=letter,
                                    tags=('type',) + self.tags)
        )

    def _open_editor_window(self):
        self._editor = editors.scene_editor(self.label, self._data)

    def _on_select(self) -> None:

        self.canvas.itemconfig(self._circle, width=self._selected_linewidth)

        self._open_editor_window()

    def _on_deselect(self):
        self.canvas.itemconfig(self._circle, width=self._unselected_linewidth)
        self._close_editor_window()

    def _close_editor_window(self):
        if self._editor:
            self._editor.destroy()
            self._editor = None

    def add_children(self, children: Iterable['SceneNode']) -> None:
        for child in children:
            self.add_child(child)

    def add_child(self, node: 'SceneNode'):
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

            self._child_edges[node] = ResolutionEdge(start_x, start_y,
                                                     final_x, final_y, self,
                                                     node)

    def __str__(self):
        child_labels = [node.label for node in self._child_edges.keys()]
        return "Node({} - {}), children: {}".format(self.label,
                                                    self.__hash__(),
                                                    child_labels)


class ResolutionEdge(CanvasAccess, Selectable):
    _selected_linewidth = 3
    _unselected_linewidth = 1

    def __init__(self, start_x, start_y, final_x, final_y, source, sink):
        super().__init__()
        Selectable.__init__(self)

        self._source = source
        self._sink = sink

        self._editor: tkinter.Tk = None

        self._line = self.canvas.create_line(start_x, start_y, final_x,
                                             final_y, arrow=tkinter.LAST,
                                             tags=('line',) + self.tags,
                                             width=self._unselected_linewidth)

    def __str__(self):
        text = 'ResolutionEdge({}): {} to {}'
        return text.format(hash(self), self._source, self._sink)

    def _on_deselect(self):
        self.canvas.itemconfig(self._line, width=self._unselected_linewidth)

    def _on_select(self):
        self.canvas.itemconfig(self._line, width=self._selected_linewidth)

    def _open_editor_window(self):
        self._editor = editors.scene_editor(self.label, self._data)


"""Editor window matching entries of nested dictionaries."""
import tkinter as tk

from editor import util
from quests.scenes.builder import scene_field_type, SceneType
from editor.util import DataType


def scene_editor(title, scene_data, **window_options):
    scene_type = SceneType(scene_data['type'])
    root = util.new_window('{} scene: {}'.format(scene_type.value, title))

    for row, field in enumerate(scene_type.arg_labels):

        category = tk.Label(root, text=field)
        category.grid(row=row)

        var = tk.StringVar(root, value=scene_data[field])

        constructor = _widget_from_data_type[scene_field_type(field)]

        value_widget = constructor(root)
        if isinstance(value_widget, (tk.Entry, tk.Label)):
            value_widget.configure(textvariable=var)
        elif isinstance(value_widget, tk.Text):
            value_widget.insert(tk.END, var.get())
            value_widget.config(height=5)
        value_widget.grid(row=row, column=1)

    return root


# class ItemEditor(tk.Frame):
#     def __init__(self, parent, item_data):
#         super().__init__(self, parent)
#
#         for row, (field, value) in enumerate(item_data.items()):
#             category = tk.Label(parent, field, text=field)
#             category.grid(row=row)
#
#             var = tk.StringVar(parent, value=value)
#
#             constructor = _widget_from_data_type[item_field_type(field)]
#
#             value_widget = constructor(parent)
#             if isinstance(value_widget, (tk.Entry, tk.Label)):
#                 value_widget.configure(textvariable=var)
#             elif isinstance(value_widget, tk.Text):
#                 value_widget.insert(tk.END, var.get())
#                 value_widget.config(height=5)
#             value_widget.grid(row=row, column=1)


_widget_from_data_type = {DataType.SHORT_TEXT: tk.Entry,
                          DataType.LONG_TEXT: tk.Text,
                          DataType.NESTED: tk.Text,
                          DataType.FIXED: tk.Label,
                          DataType.DIFFICULTY: tk.Entry}

# def item_editor(root: tk.Tk, item_data: Dict[str, str]) -> object:
#     for row, (field, value) in enumerate(item_data.items()):
#         category = tk.Label(root, field, text=field)
#         category.grid(row=row)
#
#         var = tk.StringVar(root, value=value)
#
#         constructor = _widget_from_data_type[item_field_type(field)]
#
#         value_widget = constructor(root)
#         if isinstance(value_widget, (tk.Entry, tk.Label)):
#             value_widget.configure(textvariable=var)
#         elif isinstance(value_widget, tk.Text):
#             value_widget.insert(tk.END, var.get())
#             value_widget.config(height=5)
#         value_widget.grid(row=row, column=1)

# _item_field_type = {'mod_data': DataType.SHORT_TEXT,
#                     'image_file': DataType.SHORT_TEXT}
#
#
# def item_field_type(field: str) -> DataType:
#     if field not in _item_field_type:
#         raise KeyError('Field label {} not recognized for item '
#                        'data.'.format(field))
#     return _item_field_type[field]

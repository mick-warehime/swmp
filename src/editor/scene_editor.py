"""Editor window matching entries of nested dictionaries."""
import tkinter as tk

from editor import util
from quests.scenes.builder import scene_field_type
from editor.util import DataType

_widget_from_scene_data_type = {DataType.SHORT_TEXT: tk.Entry,
                                DataType.LONG_TEXT: tk.Text,
                                DataType.NESTED: tk.Text,
                                DataType.FIXED: tk.Label,
                                DataType.DIFFICULTY: tk.Entry}


def scene_editor(title, data, **window_options):
    root = util.new_window(title)

    for row, (field, value) in enumerate(data.items()):
        category = tk.Label(root, text=field)
        category.grid(row=row)

        var = tk.StringVar(root, value=value)

        constructor = _widget_from_scene_data_type[scene_field_type(field)]

        value_widget = constructor(root)
        if isinstance(value_widget, (tk.Entry, tk.Label)):
            value_widget.configure(textvariable=var)
        elif isinstance(value_widget, tk.Text):
            value_widget.insert(tk.END, var.get())
            value_widget.config(height=5)
        value_widget.grid(row=row, column=1)

    return root

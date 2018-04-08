"""Editor window matching entries of nested dictionaries."""
import tkinter as tk

from editor import util
from quests.scenes.builder import SceneDataType, scene_field_type

_widget_from_data_type = {SceneDataType.SHORT_TEXT: tk.Entry,
                          SceneDataType.LONG_TEXT: tk.Text,
                          SceneDataType.NESTED: tk.Text,
                          SceneDataType.FIXED: tk.Label,
                          SceneDataType.DIFFICULTY: tk.Entry}


def dict_editor(title, data, **window_options):
    root = util.new_window(title)

    for row, (field, value) in enumerate(data.items()):
        category = tk.Label(root, text=field)
        category.grid(row=row)

        var = tk.StringVar(root, value=value)

        constructor = _widget_from_data_type[scene_field_type(field)]

        value_widget = constructor(root)
        if isinstance(value_widget, (tk.Entry, tk.Label)):
            value_widget.configure(textvariable=var)
        elif isinstance(value_widget, tk.Text):
            value_widget.insert(tk.END, var.get())
            value_widget.config(height=5)
        value_widget.grid(row=row, column=1)

    return root

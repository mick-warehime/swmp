import tkinter
import tkinter as tk
from enum import Enum
from typing import Callable, Any, Tuple


def close_window_after_call(fun: Callable[[Any], None],
                            window: tkinter.Tk) -> Callable[[Any], None]:
    def wrapper(*args, **kwargs) -> None:
        fun(*args, **kwargs)
        window.destroy()

    return wrapper


def assert_yaml_filename(filename):
    if filename[-4:] != '.yml':
        raise ValueError('Expected a YAML (*.yml) file.')


def draw_circle(x_center: int, y_center: int, rad: int, canvas: tkinter.Canvas,
                fill="black", tags: Tuple[str, ...] = None) -> int:
    return canvas.create_oval(x_center - rad, y_center - rad, x_center + rad,
                              y_center + rad, fill=fill, tags=tags)


class CanvasAccess(object):
    """An object with access to the current graph canvas."""

    _canvas: tkinter.Canvas = None

    def __init__(self):
        if self._canvas is None:
            raise ValueError('CanvasAccess.set_canvas must be called before '
                             'initialization.')

    @classmethod
    def set_canvas(cls, canvas: tkinter.Canvas) -> None:
        cls._canvas = canvas

    @property
    def canvas(self) -> tkinter.Canvas:
        return self._canvas


def canvas_coords_to_master_coords(canvas: tkinter.Canvas,
                                   canvas_x: int, canvas_y: int):
    """Convert canvas coordinates to the coordinates of its master Frame."""

    top_left_canvas_x = canvas.canvasx(0)
    top_left_canvas_y = canvas.canvasy(0)

    return canvas_x - top_left_canvas_x, canvas_y - top_left_canvas_y


def new_window(title: str, resizable=True) -> tkinter.Tk:
    root = tkinter.Tk()

    # # set the dimensions of the screen
    # # and where it is placed
    # if start_dimensions is not None:
    #     root.geometry('%dx%d+%d+%d' % start_dimensions)
    # else:
    #     root.geometry('+100 +100')
    root.title(title)

    if not resizable:
        root.resizable(width=False, height=False)

    return root


class DataType(Enum):
    FIXED = 'fixed'
    SHORT_TEXT = 'short'
    LONG_TEXT = 'long'
    NESTED = 'nested'
    DIFFICULTY = 'difficulty'


_widget_from_data_type = {DataType.SHORT_TEXT: tk.Entry,
                          DataType.LONG_TEXT: tk.Text,
                          DataType.NESTED: tk.Text,
                          DataType.FIXED: tk.Label,
                          DataType.DIFFICULTY: tk.Entry}


def widget_from_data_type(data_type: DataType) -> Callable:
    return _widget_from_data_type[data_type]
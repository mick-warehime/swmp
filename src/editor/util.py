import tkinter
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
    """An object with access to the current graph canvas"""

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

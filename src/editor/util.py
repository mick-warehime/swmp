import tkinter
from typing import Callable, Any


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
                fill="black") -> int:
    return canvas.create_oval(x_center - rad, y_center - rad, x_center + rad,
                              y_center + rad, fill=fill)

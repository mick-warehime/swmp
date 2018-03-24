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
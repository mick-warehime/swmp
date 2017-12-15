from typing import Callable, Dict, List, Union
import pygame as pg

MOUSE_LEFT = 0
MOUSE_CENTER = 1
MOUSE_RIGHT = 2


def call_binding(key_id: int,
                 funcs: Dict[int, Callable[..., None]],
                 filter_list: List[int]) -> None:
    key_allowed = key_id in filter_list if filter_list else True

    if key_allowed:
        funcs[key_id]()


class Controller(object):
    def __init__(self) -> None:
        # maps keys to functions
        self.bindings: Dict[int, Callable[..., None]] = {}
        self.bindings_down: Dict[int, Callable[..., None]] = {}
        self.prev_keys: List[int] = [0] * len(pg.key.get_pressed())
        self.mouse_bindings: Dict[int, Callable[..., None]] = {}

    # calls this function every frame when the key is held down
    def bind(self, key: int, binding: Callable[..., None]) -> None:
        self.bindings[key] = binding

    # calls this function on frames when this becomes pressed
    def bind_down(self, key: int, binding: Callable[..., None]) -> None:
        self.bindings_down[key] = binding

    # calls this function every frame when the mouse button is held down
    def bind_mouse(self, key: int, binding: Callable[..., None]) -> None:
        self.mouse_bindings[key] = binding

    def handle_input(self, only_handle: Union[List[int], None] = None) -> None:

        if only_handle is None:
            only_handle = []

        keys = pg.key.get_pressed()
        mouse = pg.mouse.get_pressed()
        if any(keys) or any(mouse):
            for key_id in self.bindings:
                if keys[key_id]:
                    call_binding(key_id,
                                 self.bindings,
                                 only_handle)

            for mouse_id in self.mouse_bindings:
                if mouse[mouse_id]:
                    call_binding(mouse_id,
                                 self.mouse_bindings,
                                 only_handle)

            for key_id in self.bindings_down:
                # only press if key was not down last frame
                if self.prev_keys[key_id]:
                    continue
                if keys[key_id]:
                    call_binding(key_id,
                                 self.bindings_down,
                                 only_handle)

        self.prev_keys = list(keys)

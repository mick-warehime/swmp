from typing import Callable, Dict, List
import pygame as pg


class Controller(object):
    def __init__(self) -> None:
        # maps keys to functions
        self.bindings: Dict[int, Callable[..., None]] = {}
        self.bindings_down: Dict[int, Callable[..., None]] = {}
        self.prev_keys: List[int] = [0] * len(pg.key.get_pressed())

    def bind(self, key: int, binding: Callable[..., None]) -> None:
        self.bindings[key] = binding

    def bind_down(self, key: int, binding: Callable[..., None]) -> None:
        self.bindings_down[key] = binding

    def update(self) -> None:
        keys = pg.key.get_pressed()
        for key_id in self.bindings:
            if keys[key_id]:
                self.bindings[key_id]()

        for key_id in self.bindings_down:
            if self.prev_keys[key_id]:
                continue
            if keys[key_id]:
                self.bindings_down[key_id]()

        self.prev_keys = keys

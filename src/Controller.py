from typing import Callable, Dict
import pygame as pg


class Controller(object):
    def __init__(self) -> None:
        # maps keys to functions
        self.bindings: Dict[int, Callable[..., None]] = {}

    def set_binding(self, key: int, binding: Callable[..., None]) -> None:
        self.bindings[key] = binding

    def update(self) -> None:
        keys = pg.key.get_pressed()
        for key_id in self.bindings:
            if keys[key_id]:
                self.bindings[key_id]()

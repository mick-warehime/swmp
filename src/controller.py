from typing import Callable, Dict, List, Tuple, Any
import pygame as pg
from creatures.players import Player

MOUSE_LEFT = 0
MOUSE_CENTER = 1
MOUSE_RIGHT = 2


def initialize_controller(screen: pg.Surface,
                          quit_func: Any) -> None:
    Controller._screen = screen
    Keyboard.quit_func = quit_func


class Keyboard(object):
    """Handles input/output from keyboard and mouse."""
    quit_func = None

    def __init__(self) -> None:

        # keys pressed down in the previous frame
        self._prev_keys: List[bool] = [False] * len(pg.key.get_pressed())
        self._prev_mouse: List[bool] = [False] * len(pg.mouse.get_pressed())

        # maps keys to functions
        self._bindings: Dict[int, Callable[..., None]] = {}
        self._bindings_on_press: Dict[int, Callable[..., None]] = {}
        self._mouse_bindings: Dict[int, Callable[..., None]] = {}

        # default bindings for every controller (currently only escape)
        self._bind_quit()

    # calls this function every frame when the key is held down
    def bind(self, key: int, bound_func: Callable[..., None]) -> None:
        self._bindings[key] = bound_func

    # calls this function on frames when this becomes pressed
    def bind_on_press(self, key: int, bound_func: Callable[..., None]) -> None:
        self._bindings_on_press[key] = bound_func

    # calls this function every frame when the mouse button is held down
    def bind_mouse(self, key: int, bound_func: Callable[..., None]) -> None:
        self._mouse_bindings[key] = bound_func

    def handle_input(self, allowed_keys: List[int] = None) -> None:

        if allowed_keys is None:
            allowed_keys = []

        for key_id in self._pressed_keys():
            self._call_binding(key_id, self._bindings, allowed_keys)
        for mouse_id in self._just_pressed_mouse():
            self._call_binding(mouse_id, self._mouse_bindings, allowed_keys)
        for key_id in self._just_pressed_keys():
            self._call_binding(key_id, self._bindings_on_press, allowed_keys)

    @staticmethod
    def _call_binding(key_id: int, funcs: Dict[int, Callable[..., None]],
                      allowed_keys: List[int]) -> None:
        key_allowed = key_id in allowed_keys if allowed_keys else True

        if key_allowed:
            funcs[key_id]()

    @property
    def mouse_just_clicked(self) -> bool:
        mouse = pg.mouse.get_pressed()
        return mouse[MOUSE_LEFT] and not self._prev_mouse[MOUSE_LEFT]

    @property
    def mouse_pos(self) -> Tuple[int, int]:
        return pg.mouse.get_pos()

    def set_previous_input(self) -> None:
        self._prev_keys = list(pg.key.get_pressed())
        self._prev_mouse = list(pg.mouse.get_pressed())

    def _bind_quit(self) -> None:
        self.bind(pg.K_ESCAPE, self.quit_func)

    def _just_pressed_keys(self) -> List[int]:
        key_array = pg.key.get_pressed()
        just_pressed_keys = []
        for key_id in self._bindings_on_press:
            if not self._prev_keys[key_id] and key_array[key_id]:
                just_pressed_keys.append(key_id)
        return just_pressed_keys

    def _just_pressed_mouse(self) -> List[int]:
        mouse_array = pg.mouse.get_pressed()
        just_pressed_mouse = []
        for button_id in self._mouse_bindings:
            if mouse_array[button_id] and not self._prev_mouse[button_id]:
                just_pressed_mouse.append(button_id)
        return just_pressed_mouse

    def _pressed_keys(self) -> List[int]:
        key_array = pg.key.get_pressed()
        pressed_keys = [keyid for keyid in self._bindings if key_array[keyid]]
        return pressed_keys


class Controller(object):
    _screen = None

    def __init__(self) -> None:
        self.keyboard = Keyboard()

        self.player: Player = None

    def set_player(self, new_player: Player) -> None:
        self.player.inventory = new_player.inventory
        self.player.status = new_player.status

    # def resolved_conflict_index(self) -> int:
    #     raise NotImplementedError()

    def game_over(self) -> bool:
        raise NotImplementedError()

    # def should_exit(self) -> bool:
    #     raise NotImplementedError()

    def draw(self) -> None:
        raise NotImplementedError

    def update(self) -> None:
        raise NotImplementedError

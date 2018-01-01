from typing import Callable, Dict, List, Union, Tuple, Any
import pygame as pg
from creatures.players import Player

MOUSE_LEFT = 0
MOUSE_CENTER = 1
MOUSE_RIGHT = 2
NOT_CLICKED = (-1, -1)


def initialize_controller(screen: pg.Surface,
                          quit_func: Any) -> None:
    Controller._screen = screen
    Controller._quit_func = quit_func


def call_binding(key_id: int,
                 funcs: Dict[int, Callable[..., None]],
                 filter_list: List[int]) -> None:
    key_allowed = key_id in filter_list if filter_list else True

    if key_allowed:
        funcs[key_id]()


class Controller(object):
    _screen = None
    _quit_func = None

    def __init__(self) -> None:

        # keys pressed down in the previous frame
        self._prev_keys: List[int] = [0] * len(pg.key.get_pressed())
        self._prev_mouse: List[int] = [0] * len(pg.mouse.get_pressed())

        # maps keys to functions
        self.bindings: Dict[int, Callable[..., None]] = {}
        self.bindings_on_press: Dict[int, Callable[..., None]] = {}
        self.mouse_bindings: Dict[int, Callable[..., None]] = {}

        # default bindings for every controller (currently only escape)
        self.bind_quit()
        self.n_default_bindings = 1

        self.player: Player = None

    # calls this function every frame when the key is held down
    def bind(self, key: int, binding: Callable[..., None]) -> None:
        self.bindings[key] = binding

    # calls this function on frames when this becomes pressed
    def bind_on_press(self, key: int, binding: Callable[..., None]) -> None:
        self.bindings_on_press[key] = binding

    # calls this function every frame when the mouse button is held down
    def bind_mouse(self, key: int, binding: Callable[..., None]) -> None:
        self.mouse_bindings[key] = binding

    def handle_input(self, only_handle: Union[List[int], None] = None) -> None:

        if only_handle is None:
            only_handle = []

        keys = pg.key.get_pressed()
        mouse = pg.mouse.get_pressed()
        if any(keys) or any(mouse):
            for key_id in self._pressed_keys(keys):
                call_binding(key_id,
                             self.bindings,
                             only_handle)
            for mouse_id in self._just_pressed_mouse(mouse):
                call_binding(mouse_id,
                             self.mouse_bindings,
                             only_handle)
            for key_id in self._just_pressed_keys(keys):
                call_binding(key_id,
                             self.bindings_on_press,
                             only_handle)

    def _just_pressed_keys(self, key_array: List[bool]) -> List[int]:
        just_pressed_keys = []
        for key_id in self.bindings_on_press:
            if not self._prev_keys[key_id] and key_array[key_id]:
                just_pressed_keys.append(key_id)
        return just_pressed_keys

    def _just_pressed_mouse(self, mouse_array: List[bool]) -> List[int]:
        just_pressed_mouse = []
        for button_id in self.mouse_bindings:
            if mouse_array[button_id] and not self._prev_mouse[button_id]:
                just_pressed_mouse.append(button_id)
        return just_pressed_mouse

    def _pressed_keys(self, key_array: List[bool]) -> List[int]:
        pressed_keys = [key_id for key_id in self.bindings if key_array[key_id]]
        return pressed_keys

    def get_clicked_pos(self) -> Tuple[int, int]:
        mouse = pg.mouse.get_pressed()

        # determine if we clicked this frame
        if mouse[MOUSE_LEFT] and not self._prev_mouse[MOUSE_LEFT]:
            return pg.mouse.get_pos()

        return NOT_CLICKED

    def set_previous_input(self) -> None:
        keys = pg.key.get_pressed()
        mouse = pg.mouse.get_pressed()
        self._prev_keys = list(keys)
        self._prev_mouse = list(mouse)

    def bind_quit(self) -> None:
        self.bind(pg.K_ESCAPE, self._quit_func)

    def set_player(self, player: Player) -> None:
        self.player.backpack = player.backpack
        self.player.increment_health(-self.player.health)
        self.player.increment_health(player.health)
        self.player.active_mods = player.active_mods

    def resolved_conflict_index(self) -> int:
        raise NotImplementedError()

    def game_over(self) -> bool:
        raise NotImplementedError()

    def should_exit(self) -> bool:
        raise NotImplementedError()

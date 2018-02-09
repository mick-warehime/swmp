import controller
from typing import Dict, Callable, List
import pygame as pg
import images
import settings
import draw_utils


class DecisionView(object):
    """Draws text for decision scenes"""

    def __init__(self, screen: pg.Surface, text_lines: List[str]) -> None:
        self._screen = screen
        self._text_lines = text_lines

    def draw(self) -> None:
        self._screen.fill(settings.BLACK)

        title_font = images.get_font(images.ZOMBIE_FONT)

        n_texts = len(self._text_lines) + 1
        for idx, text in enumerate(self._text_lines, 0):
            draw_utils.draw_text(self._screen, text, title_font,
                                 40, settings.WHITE, settings.WIDTH / 2,
                                 settings.HEIGHT * (idx + 1) / n_texts,
                                 align="center")
        pg.display.flip()


class DecisionController(controller.Controller):
    # takes a list of strings of the form [Prompt, option 1, ..., option n]
    def __init__(self, prompt: str, options: List[str]) -> None:

        super().__init__()

        self._prompt = prompt
        self.choice = None

        self.options_keys = [pg.K_0, pg.K_1, pg.K_2,
                             pg.K_3, pg.K_4, pg.K_5,
                             pg.K_6, pg.K_7, pg.K_8,
                             pg.K_9]

        self.option_texts: Dict[int, str] = {}

        self.keys_to_handle = self.options_keys + [pg.K_ESCAPE]

        for idx, option in enumerate(options, 1):
            self._bind_option_key(idx, option)

        self._view = DecisionView(self._screen, self._get_texts())

    def update(self) -> None:
        self.keyboard.handle_input(allowed_keys=self.keys_to_handle)

    def draw(self) -> None:
        self._view.draw()

    def _bind_option_key(self, idx: int, option: str) -> None:

        assert idx < 10, 'decision must have less than 10 options'
        assert idx >= 0, 'decision must be a >= 0'

        key = self.options_keys[idx]
        self.keyboard.bind(key, self._get_choice_function(idx))
        self.option_texts[idx] = option

    def _get_choice_function(self, key_idx: int) -> Callable[..., None]:
        def choice_func() -> None:
            self.choice = key_idx - 1

        return choice_func

    def _get_texts(self) -> List[str]:

        option_texts = [self._prompt, '', '']
        for idx, option in self.option_texts.items():
            option_texts.append('{} - {}'.format(idx, option))

        return option_texts

    def wait_for_decision(self) -> None:
        self.draw()
        while self.choice is None:
            pg.event.wait()
            self.update()

    def resolved_conflict_index(self) -> int:
        return self.choice

    # can't lose from decision screen
    def game_over(self) -> bool:
        return False

    def should_exit(self) -> bool:
        return self.choice is not None

        # decision controllers should take the option dict
        # dungeon controllers should take the next scene name as a param
        # all controllers should implement a function called next scene name

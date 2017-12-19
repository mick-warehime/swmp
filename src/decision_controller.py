import controller
from typing import Dict, Callable, List
import pygame as pg
import images
import settings
from draw_utils import draw_text


class DecisionController(controller.Controller):
    # takes a list of strings of the form [Prompt, option 1, ..., option n]
    def __init__(self,
                 screen: pg.Surface,
                 prompt: str,
                 options: List[str]) -> None:

        super(DecisionController, self).__init__()

        self._screen = screen
        self._prompt = prompt
        self.choice = -1

        self.options_keys = [pg.K_0, pg.K_1, pg.K_2,
                             pg.K_3, pg.K_4, pg.K_5,
                             pg.K_6, pg.K_7, pg.K_8,
                             pg.K_9]

        self.options: Dict[int, str] = {}

        for idx, option in enumerate(options, 1):
            self.set_option(idx, option)

    def set_option(self, idx: int, option: str) -> None:

        assert idx < 10, 'decision must have less than 10 options'
        assert idx >= 0, 'decision must be a >= 0'

        key = self.options_keys[idx]
        self.bind(key, self.get_choice_function(idx))
        self.options[idx] = option

    def get_choice_function(self, key_idx: int) -> Callable[..., None]:
        def choice_func() -> None:
            self.choice = key_idx

        return choice_func

    def set_choice(self, choice: int) -> None:
        self.choice = choice

    def update(self) -> None:
        self.handle_input()

    def draw(self) -> None:
        self._screen.fill(settings.BLACK)

        texts = self.get_text()
        title_font = images.get_font(images.ZOMBIE_FONT)

        n_texts = len(texts) + 1
        for idx, text in enumerate(texts, 1):
            draw_text(self._screen, text, title_font,
                      40, settings.WHITE, settings.WIDTH / 2,
                      settings.HEIGHT * idx / n_texts, align="center")
        pg.display.flip()

    def get_text(self) -> List[str]:

        option_texts = [self._prompt, '', '']
        for idx in self.options:
            option = self.options[idx]
            option_texts.append('{} - {}'.format(idx, option))

        return option_texts

    def wait_for_decision(self) -> int:

        while self.choice == -1:
            pg.event.wait()
            self.handle_input()

        return self.choice

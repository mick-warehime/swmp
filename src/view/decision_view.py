from typing import List

import pygame as pg

import settings
from view import images, draw_utils


def _break_string_into_lines(max_chars_per_line: int,
                             string: str) -> List[str]:
    all_words = string.split(' ')
    lines = []
    current_line_length = 0
    current_line = ''
    for word in all_words:
        if len(word) + current_line_length + 1 > max_chars_per_line:
            lines.append(current_line)
            current_line = ''
            current_line_length = 0

        current_line += word + ' '
        current_line_length += len(word) + 1
    lines.append(current_line)

    return lines


class DecisionView(object):
    """Draws text for decision and transition scenes."""

    def __init__(self, screen: pg.Surface, prompt: str,
                 options: List[str], enumerate_options: bool = True) -> None:
        self._screen = screen

        max_chars_per_line = 70

        prompt_lines = _break_string_into_lines(max_chars_per_line, prompt)

        if enumerate_options:
            style = '{} - {}'
            options = [style.format(k + 1, opt) for k, opt in
                       enumerate(options)]
        self._text_lines = prompt_lines + [''] * 2 + options

    def draw(self) -> None:
        self._screen.fill(settings.BLACK)

        title_font = images.get_font(images.IMPACTED_FONT)

        num_lines = len(self._text_lines) + 1
        for idx, text in enumerate(self._text_lines, 0):
            draw_utils.draw_text(self._screen, text, title_font,
                                 24, settings.WHITE, settings.WIDTH / 2,
                                 settings.HEIGHT * (idx + 1) / num_lines,
                                 align="center")
        pg.display.flip()

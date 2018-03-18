import pygame as pg


def draw_text(screen: pg.Surface, text: str, font_name: str,
              size: int, color: tuple, x: int, y: int,
              align: str = "topleft") -> None:
    fnt = pg.font.Font(font_name, size)
    text_surface = fnt.render(text, True, color)
    text_rect = text_surface.get_rect(**{align: (x, y)})
    screen.blit(text_surface, text_rect)

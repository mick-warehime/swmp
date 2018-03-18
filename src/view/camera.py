import pygame as pg

from settings import WIDTH, HEIGHT


class Camera:
    def __init__(self, width: int, height: int) -> None:
        self.rect = pg.Rect(0, 0, width, height)

    def get_shifted_rect(self, sprite: pg.sprite.Sprite) -> pg.Rect:
        return self.shift_by_topleft(sprite.rect)

    def shift_by_topleft(self, rect: pg.Rect) -> pg.Rect:
        return rect.move(self.rect.topleft)

    def update(self, target: pg.sprite.Sprite) -> None:
        x = -target.rect.centerx + int(WIDTH / 2)
        y = -target.rect.centery + int(HEIGHT / 2)

        # limit scrolling to map size
        x = min(0, x)  # left
        y = min(0, y)  # top
        x = max(-(self.rect.width - WIDTH), x)  # right
        y = max(-(self.rect.height - HEIGHT), y)  # bottom
        self.rect = pg.Rect(x, y, self.rect.width, self.rect.height)

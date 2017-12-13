import pygame as pg
import pytmx

from settings import WIDTH, HEIGHT


def collide_hit_rect(one: pg.sprite.Sprite, two: pg.sprite.Sprite) -> bool:
    return one.hit_rect.colliderect(two.rect)


class TiledMap:
    def __init__(self, filename: str) -> None:
        tm = pytmx.load_pygame(filename, pixelalpha=True)
        self.width = tm.width * tm.tilewidth
        self.height = tm.height * tm.tileheight
        self.tmxdata = tm

    def render(self, surface: pg.Surface) -> None:
        ti = self.tmxdata.get_tile_image_by_gid
        for layer in self.tmxdata.visible_layers:
            if isinstance(layer, pytmx.TiledTileLayer):
                for x, y, gid, in layer:
                    tile = ti(gid)
                    if tile:
                        surface.blit(tile, (x * self.tmxdata.tilewidth,
                                            y * self.tmxdata.tileheight))

    def make_map(self) -> pg.Surface:
        temp_surface = pg.Surface((self.width, self.height))
        self.render(temp_surface)
        return temp_surface


class Camera:
    def __init__(self, width: int, height: int) -> None:
        self.camera = pg.Rect(0, 0, width, height)
        self.width = width
        self.height = height

    def apply(self, entity: pg.sprite.Sprite) -> None:
        return entity.rect.move(self.camera.topleft)

    def apply_rect(self, rect: pg.Rect) -> pg.Rect:
        return rect.move(self.camera.topleft)

    def update(self, target: pg.sprite.Sprite) -> None:
        x = -target.rect.centerx + int(WIDTH / 2)
        y = -target.rect.centery + int(HEIGHT / 2)

        # limit scrolling to map size
        x = min(0, x)  # left
        y = min(0, y)  # top
        x = max(-(self.width - WIDTH), x)  # right
        y = max(-(self.height - HEIGHT), y)  # bottom
        self.camera = pg.Rect(x, y, self.width, self.height)

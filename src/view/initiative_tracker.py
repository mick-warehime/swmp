from typing import List, Tuple
import pygame as pg
import settings
from creatures.party import Party
from view.screen import ScreenAccess
from view.draw_utils import draw_text
import images

NO_SELECTION = -1


class InitiativeTracker(ScreenAccess):
    def __init__(self, party: Party) -> None:
        super().__init__()

        # HUD size & location
        self._tracker_width = 283
        self._tracker_height = 68
        tracker_x = (settings.WIDTH - self._tracker_width) / 2.0
        tracker_y = settings.HEIGHT - self._tracker_height
        self._tracker_pos = (tracker_x, tracker_y)
        self._tracker_bar_offset = 0
        self._bar_length = 20
        self._bar_height = 75
        self.rect = pg.Rect(tracker_x,
                            tracker_y,
                            self._tracker_width,
                            self._tracker_height)

        self._party = party
        self._character_rects = self._generate_character_rects()

        self._backpack_hidden = True

    def draw(self) -> None:
        self._draw_tracker_base()
        self._draw_images()

    def collide_point(self, pos: Tuple[int, int]) -> bool:
        x, y = pos
        if self.rect.collidepoint(x, y):
            return True

        in_backpack = self.backpack_base.collidepoint(x, y)
        backpack_hidden = self._backpack_hidden
        return in_backpack and not backpack_hidden

    def _draw_tracker_base(self) -> None:

        # tracker base
        pg.draw.rect(self.screen, settings.HUDGREY, self.rect)

    def _draw_images(self) -> None:

        for idx, r in enumerate(self._character_rects):
            col = settings.HUDDARK
            if self._party.member_is_active(idx):
                col = (200, 200, 200)

            # outline
            pg.draw.rect(self.screen, col, r, 2)

            # image
            member = self._party[idx]
            img = pg.transform.scale(member.image, (64, 64))
            self.screen.blit(img, r)

            # initiative
            font = images.get_font(images.IMPACTED_FONT)
            draw_text(self.screen, str(member.initiative), font, 13, (250, 50, 50), r.x + 3, r.y)

    def _generate_character_rects(self) -> List[pg.Rect]:
        mod_size = 62
        x, y = self._tracker_pos
        rects: List[pg.Rect] = []
        i = 0
        for _ in range(len(self._party)):
            x_i = x + i * (mod_size + 3)
            fill_rect = pg.Rect(x_i + 3, y + 3, mod_size, mod_size)
            rects.append(fill_rect)
            i += 1

        return rects

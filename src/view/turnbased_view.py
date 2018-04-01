from typing import List, Tuple

import pygame as pg
from pygame.math import Vector2
from pygame.rect import Rect
from pygame.sprite import Sprite

import model
import settings
from creatures.party import Party
from view.screen import ScreenAccess
from tilemap import TiledMap
from view import images
from view.camera import Camera
from view.initiative_tracker import InitiativeTracker

NO_SELECTION = -1


class TurnBasedView(model.GroupsAccess, ScreenAccess):
    def __init__(self, party: Party) -> None:
        super().__init__()

        dim_screen = pg.Surface(self.screen.get_size()).convert_alpha()
        dim_screen.fill((0, 0, 0, 180))

        self.camera: Camera = Camera(800, 600)

        self._draw_debug = False
        self.draw_teleport_text = False

        self._fog = pg.Surface((settings.WIDTH, settings.HEIGHT))
        self._fog.fill(settings.NIGHT_COLOR)

        # lighting effect for night mode
        self._light_mask = images.get_image(images.LIGHT_MASK)
        self._light_rect = self._light_mask.get_rect()

        self.title_font = images.get_font(images.ZOMBIE_FONT)

        self._party = party
        self._initiative_tracker = InitiativeTracker(party)

        self._move_options = None

    def set_camera_range(self, width: int, height: int) -> None:
        x, y = self.camera.rect.x, self.camera.rect.y
        self.camera.rect = Rect(x, y, width, height)

    def draw(self, tile_map: TiledMap) -> None:

        self.camera.update(self._party[0])

        self.screen.blit(tile_map.img, self.camera.get_shifted_rect(tile_map))

        for member in self._party:
            sprite = member
            self._draw_sprite(sprite)

        if self._draw_debug:
            self._draw_debug_rects()

        self._draw_move_options()

        member = self._party.active_member
        self._highlight_rect(member.rect)



        self._initiative_tracker.draw()

    def _draw_sprite(self, sprite: Sprite) -> None:
        image = sprite.image
        rect = image.get_rect().copy()
        new_center = Vector2(sprite.pos)
        new_center.x += self.camera.rect.topleft[0]
        new_center.y += self.camera.rect.topleft[1]
        rect.center = new_center

        if self._rect_on_screen(rect):
            self.screen.blit(image, rect)

    def _rect_on_screen(self, rect: Rect) -> bool:
        return self.screen.get_rect().colliderect(rect)

    def _highlight_rect(self, rect: pg.Surface, red: bool = False) -> None:
        shifted_rect = self.camera.shift_by_topleft(rect)
        if self._rect_on_screen(shifted_rect):
            if red:
                pg.draw.rect(self.screen, settings.RED, shifted_rect, 1)
            else:
                pg.draw.rect(self.screen, settings.CYAN, shifted_rect, 1)

    def _draw_debug_rects(self) -> None:
        for sprite in self.groups.all_sprites:
            if hasattr(sprite, 'motion'):
                rect = sprite.motion.hit_rect
            else:
                rect = sprite.rect
            self._highlight_rect(rect)

        for obstacle in self.groups.walls:
            assert obstacle not in self.groups.all_sprites
            shifted_rect = self.camera.shift_by_topleft(obstacle.rect)
            if self._rect_on_screen(shifted_rect):
                self._highlight_rect(shifted_rect)

        for member in self._party:
            shifted_rect = self.camera.shift_by_topleft(member.rect)
            if self._rect_on_screen(shifted_rect):
                self._highlight_rect(shifted_rect)

    def _draw_move_options(self) -> None:
        if self._party.active_member_moved:
            return

        self._move_option_rects()
        for rect in self._move_options:
            self._highlight_rect(rect, red=True)

    def _move_option_rects(self) -> List[pg.Surface]:
        if self._move_options:
            return

        rects: List[pg.Surface] = []
        member = self._party.active_member
        move_range = range(-member.speed, member.speed+1)
        for i in move_range:
            for j in move_range:
                if self._party.active_member.can_reach(i, j):
                    r = member.rect.move(i * 32, j * 32)
                    rects.append(r)
        self._move_options = rects

    def toggle_debug(self) -> None:
        self._draw_debug = not self._draw_debug

    def _try_move(self, pos: Tuple[int, int]) -> None:
        if self._party.active_member_moved:
            return

        for rect in self._move_options:
            # move to new location
            if rect.collidepoint(pos[0], pos[1]):
                self._party.active_member.pos = rect.center
                self._move_options = None

        self._party.next_member()


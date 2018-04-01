from typing import List, Tuple

import pygame as pg
from pygame.math import Vector2
from pygame.rect import Rect
from pygame.sprite import Sprite
import math
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

        self._move_options: List[pg.Surface] = []

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
        if not self._move_options:
            return

        for rect in self._move_options:
            self._highlight_rect(rect, red=True)

    def _move_option_rects(self) -> None:
        if self._move_options:
            return

        rects: List[pg.Surface] = []
        member = self._party.active_member
        move_range = range(-member.speed, member.speed + 1)
        for i in move_range:
            for j in move_range:
                dest_rect = member.rect.move(i * 32, j * 32)
                if self._party.active_member.can_reach(i, j) and \
                        self._path_is_clear(member.rect, dest_rect):
                    rects.append(dest_rect)

        self._move_options = rects

    def _path_is_clear(self, rect1: pg.Surface, rect2: pg.Surface) -> bool:
        test_points = self._points_between(rect1, rect2)
        for point in test_points:
            for wall in self.groups.walls:
                if wall.rect.collidepoint(point[0], point[1]):
                    return False

        return True

    def _points_between(self, rect1: pg.Surface, rect2: pg.Surface)\
            -> List[Tuple[int, int]]:

        p1 = rect1.center
        p2 = rect2.center

        points = [p1, p2]
        dist = math.sqrt((p1[0] - p2[0]) ** 2 + (p1[1] - p2[1]) ** 2)
        step_size = 5.0
        num_steps = int(dist / step_size)
        for i in range(1, num_steps - 1):
            s = i / num_steps
            x = p1[0] * s + p2[0] * (1 - s)
            y = p1[1] * s + p2[1] * (1 - s)
            points.append((x, y))

        return points

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
                return

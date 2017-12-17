import unittest
import view
import pygame
import settings


class ViewTest(unittest.TestCase):
    def setUp(self) -> None:
        screen = pygame.display.set_mode((settings.WIDTH, settings.HEIGHT))
        self.view = view.DungeonView(screen)

    def test_click_skill(self) -> None:

        for idx, r in enumerate(self.view.skill_rects):
            x = r.centerx
            y = r.centery
            self.view.try_click_skill((x, y))
            self.assertEqual(self.view._selected_skill, idx)

        self.view.try_click_skill((0, 0))
        self.assertEqual(self.view._selected_skill, -1)

    def test_click_item(self) -> None:
        for idx, r in enumerate(self.view.backpack_rects):
            x = r.centerx
            y = r.centery
            self.view.try_click_item((x, y))
            self.assertEqual(self.view._selected_item, idx)

        self.view.try_click_item((0, 0))
        self.assertEqual(self.view._selected_item, -1)

    def test_click_twice_reset(self) -> None:
        r = self.view.backpack_rects[0]
        x = r.centerx
        y = r.centery
        self.view.try_click_item((x, y))
        self.assertEqual(self.view._selected_item, 0)
        self.view.try_click_item((x, y))
        self.assertEqual(self.view._selected_item, -1)

import unittest
from dungeon_controller import Conflict
from pygame.sprite import Group, Sprite


class ConflictTest(unittest.TestCase):
    def test_kill_all_conflict(self) -> None:
        # conflict = kill 100 enemies
        g = Group()
        n_sprites = 100
        sprites = []
        for _ in range(n_sprites):
            s = Sprite()
            Sprite.__init__(s, g)
            sprites.append(s)

        # verify we start with a conflict
        c = Conflict(g)
        self.assertFalse(c.is_resolved())

        # verify the conflict isn't over after the first
        # 99 kills
        for i in range(n_sprites - 1):
            sprites[i].kill()
            self.assertFalse(c.is_resolved())

        # verify killing the last mob resolves the conflict
        sprites[-1].kill()
        self.assertTrue(c.is_resolved())

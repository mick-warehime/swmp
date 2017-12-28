import unittest
import tilemap
from model import Conflict
from pygame.sprite import Sprite
from testing_utilities import TiledmapObject


class ConflictTest(unittest.TestCase):
    def test_kill_all_conflict(self) -> None:
        # conflict = kill 100 enemies
        c = Conflict()
        g = c.group
        n_sprites = 100
        sprites = []
        for _ in range(n_sprites):
            s = Sprite()
            Sprite.__init__(s, g)
            sprites.append(s)

        # verify we start with a conflict
        self.assertFalse(c.is_resolved())

        # verify the conflict isn't over after the first
        # 99 kills
        for i in range(n_sprites - 1):
            sprites[i].kill()
            self.assertFalse(c.is_resolved())

        # verify killing the last mob resolves the conflict
        sprites[-1].kill()
        self.assertTrue(c.is_resolved())

    def test_conflict_object(self) -> None:
        # a tiledmap object with the custom field conflict = '1'
        conflict_name = '1'
        obj = TiledmapObject(tilemap.ObjectType.WAYPOINT, conflict_name)
        map_obj = tilemap.MapObject(obj)
        self.assertEqual(map_obj.conflict, conflict_name)

        # tiled map with no conflict field
        obj = TiledmapObject(tilemap.ObjectType.WAYPOINT)
        map_obj = tilemap.MapObject(obj)
        self.assertEqual(map_obj.conflict, tilemap.NOT_CONFLICT)

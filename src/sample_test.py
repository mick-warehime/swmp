from unittest import TestCase
from sample import my_func

class SampleTest(TestCase):
    def test_stupid(self) -> None:
        self.assertTrue(True)

    def test_my_func(self):
        res = my_func(1, 2)
        self.assertEqual(res, -1)

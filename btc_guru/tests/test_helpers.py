import unittest
from helpers import grouper


class HelpersTest(unittest.TestCase):

    def test_grouper(self):
        data = [1, 2, 3, 4, 5]
        grouped = grouper(data, 2)
        self.assertEqual([1, 2], list(next(grouped)))
        self.assertEqual([3, 4], list(next(grouped)))
        self.assertEqual([5, None], list(next(grouped)))
        with self.assertRaises(StopIteration):
            next(grouped)

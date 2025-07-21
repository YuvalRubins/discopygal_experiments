import sys
import json
import math
import unittest

sys.path.append('src')

from discopygal.bindings import *
from discopygal.geometry_utils.conversions import *

TEST_CD_SCENE = './examples/scenes/test_collision_detection.json'

class TestNearestNeighbors(unittest.TestCase):
    def test_Point_d_to_Point_2_list(self):
        point_d = Point_d(8, [FT(1) for _ in range(8)])
        res = Point_d_to_Point_2_list(point_d)
        self.assertEqual(len(res), 4)
        self.assertIn(Point_2(FT(1), FT(1)), res)

    def test_Point_2_list_to_Point_d(self):
        points = [
            Point_2(FT(0), FT(1)),
            Point_2(FT(2), FT(3)),
            Point_2(FT(4), FT(5)),
            Point_2(FT(6), FT(7)),
        ]
        point_d = Point_d(8, [FT(i) for i in range(8)])
        res = Point_2_list_to_Point_d(points)
        self.assertEqual(res, point_d)

if __name__ == "__main__":
    unittest.main()
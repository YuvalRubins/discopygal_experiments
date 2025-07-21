import sys
import json
import math
import unittest

sys.path.append('src')

from discopygal.bindings import *
from discopygal.solvers_infra import *
from discopygal.solvers_infra.metrics import *
from discopygal.solvers_infra.samplers import *
from discopygal.solvers_infra.nearest_neighbors import *
from discopygal.geometry_utils import collision_detection as cd

class TestSamplers(unittest.TestCase):
    def test_uniform_monte_carlo(self):
        """
        Test uniform sampler by trying to compute the value of pi
        """
        disc = ObstacleDisc(Point_2(FT(0), FT(0)), FT(1))
        robot = RobotDisc(FT(0), Point_2(FT(0), FT(0)), Point_2(FT(0), FT(0))) # Point robot
        obj_cd = cd.ObjectCollisionDetection([disc], robot)
        scene = Scene([disc], [robot])
        
        num_tests = 10
        success = 0
        for _ in range(num_tests):
            sampler = Sampler_Uniform(scene)
            samples = 10000
            cnt = 0
            for _ in range(samples):
                sample = sampler.sample()
                if not obj_cd.is_point_valid(sample):
                    cnt += 1 # If point in circle increment counter
            pi = cnt / samples * 4 # Percent inside circle's bounding box
            if abs(pi - 3.14159265) < 0.01:
                success += 1
        self.assertGreater(success, 0) # At least one of the tests should succeed..
        

if __name__ == "__main__":
    unittest.main()
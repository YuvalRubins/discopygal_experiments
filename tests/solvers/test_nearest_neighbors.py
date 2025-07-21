import sys
import json
import math
import unittest

sys.path.append('src')

from discopygal.bindings import *
from discopygal.solvers_infra import *
from discopygal.solvers_infra.metrics import *
from discopygal.solvers_infra.nearest_neighbors import *

class TestNearestNeighbors(unittest.TestCase):
    def test_euclidean_metric(self):
        # Test Point_2
        p = Point_2(FT(0),FT(0))
        q = Point_2(FT(1),FT(1))
        eps = 0.001
        d = Metric_Euclidean.dist(p, q).to_double()
        self.assertLess(abs(d - math.sqrt(2)), eps)

        # Test Point_d (with d=8)
        p = Point_d(8, [FT(x) for x in [0] * 8])
        q = Point_d(8, [FT(x) for x in [1] * 8])
        eps = 0.001
        d = Metric_Euclidean.dist(p, q).to_double()
        self.assertLess(abs(d - math.sqrt(8)), eps)

    def test_nn_sklearn_point_2(self):
        """
        Check that nearest neighbors (with sklearn implementation) works for Point_2
        """
        k = 3
        radius = FT(5)
        points = [
            Point_2(FT(4), FT(0)),
            Point_2(FT(-4), FT(0)),
            Point_2(FT(40), FT(0)),
            Point_2(FT(-40), FT(0)),
            Point_2(FT(1), FT(0))]
        query = Point_2(FT(0), FT(0))
        nn = NearestNeighbors_sklearn(Metric_Euclidean)
        nn.fit(points)

        # Test knn
        knn = nn.k_nearest(query, k)
        self.assertEqual(len(knn), k)
        self.assertIn(Point_2(FT(4), FT(0)), knn)
        self.assertIn(Point_2(FT(-4), FT(0)), knn)
        self.assertIn(Point_2(FT(1), FT(0)), knn)
        self.assertNotIn(Point_2(FT(-40), FT(0)), knn)

        # Test nearest in radius (=nir)
        nir = nn.nearest_in_radius(query, radius)
        self.assertEqual(len(knn), 3)
        self.assertIn(Point_2(FT(4), FT(0)), nir)
        self.assertIn(Point_2(FT(-4), FT(0)), nir)
        self.assertIn(Point_2(FT(1), FT(0)), nir)
        self.assertNotIn(Point_2(FT(-40), FT(0)), nir)

    def test_nn_sklearn_point_d(self):
        """
        Check that nearest neighbors (with sklearn implementation) works for Point_d
        """
        k = 3
        radius = FT(5)
        points = [
            Point_d(2, [FT(n) for n in [4, 0]]),
            Point_d(2, [FT(n) for n in [-4, 0]]),
            Point_d(2, [FT(n) for n in [40, 0]]),
            Point_d(2, [FT(n) for n in [-40, 0]]),
            Point_d(2, [FT(n) for n in [1, 0]])]
        query = Point_d(2, [FT(n) for n in [0, 0]])
        nn = NearestNeighbors_sklearn(Metric_Euclidean)
        nn.fit(points)

        # Test knn
        knn = nn.k_nearest(query, k)
        self.assertEqual(len(knn), k)
        self.assertIn(Point_d(2, [FT(n) for n in [4, 0]]), knn)
        self.assertIn(Point_d(2, [FT(n) for n in [-4, 0]]), knn)
        self.assertIn(Point_d(2, [FT(n) for n in [1, 0]]), knn)
        self.assertNotIn(Point_d(2, [FT(n) for n in [-40, 0]]), knn)

        # Test nearest in radius (=nir)
        nir = nn.nearest_in_radius(query, radius)
        self.assertEqual(len(knn), 3)
        self.assertIn(Point_d(2, [FT(n) for n in [4, 0]]), nir)
        self.assertIn(Point_d(2, [FT(n) for n in [-4, 0]]), nir)
        self.assertIn(Point_d(2, [FT(n) for n in [1, 0]]), nir)
        self.assertNotIn(Point_d(2, [FT(n) for n in [-40, 0]]), nir)


    def test_nn_CGAL_point_2(self):
        """
        Check that nearest neighbors (with CGAL implementation) works for Point_2
        """
        k = 3
        radius = FT(5)
        points = [
            Point_2(FT(4), FT(0)),
            Point_2(FT(-4), FT(0)),
            Point_2(FT(40), FT(0)),
            Point_2(FT(-40), FT(0)),
            Point_2(FT(1), FT(0))]
        query = Point_2(FT(0), FT(0))
        nn = NearestNeighbors_CGAL(Metric_Euclidean)
        nn.fit(points)

        # Test knn
        knn = nn.k_nearest(query, k)
        self.assertEqual(len(knn), k)
        self.assertIn(Point_2(FT(4), FT(0)), knn)
        self.assertIn(Point_2(FT(-4), FT(0)), knn)
        self.assertIn(Point_2(FT(1), FT(0)), knn)
        self.assertNotIn(Point_2(FT(-40), FT(0)), knn)

        # Test nearest in radius (=nir)
        nir = nn.nearest_in_radius(query, radius)
        self.assertEqual(len(knn), 3)
        self.assertIn(Point_2(FT(4), FT(0)), nir)
        self.assertIn(Point_2(FT(-4), FT(0)), nir)
        self.assertIn(Point_2(FT(1), FT(0)), nir)
        self.assertNotIn(Point_2(FT(-40), FT(0)), nir)

    def test_nn_CGAL_point_d(self):
        """
        Check that nearest neighbors (with CGAL implementation) works for Point_d
        """
        k = 3
        radius = FT(5)
        points = [
            Point_d(2, [FT(n) for n in [4, 0]]),
            Point_d(2, [FT(n) for n in [-4, 0]]),
            Point_d(2, [FT(n) for n in [40, 0]]),
            Point_d(2, [FT(n) for n in [-40, 0]]),
            Point_d(2, [FT(n) for n in [1, 0]])]
        query = Point_d(2, [FT(n) for n in [0, 0]])
        nn = NearestNeighbors_sklearn(Metric_Euclidean)
        nn.fit(points)

        # Test knn
        knn = nn.k_nearest(query, k)
        self.assertEqual(len(knn), k)
        self.assertIn(Point_d(2, [FT(n) for n in [4, 0]]), knn)
        self.assertIn(Point_d(2, [FT(n) for n in [-4, 0]]), knn)
        self.assertIn(Point_d(2, [FT(n) for n in [1, 0]]), knn)
        self.assertNotIn(Point_d(2, [FT(n) for n in [-40, 0]]), knn)

        # Test nearest in radius (=nir)
        nir = nn.nearest_in_radius(query, radius)
        self.assertEqual(len(knn), 3)
        self.assertIn(Point_d(2, [FT(n) for n in [4, 0]]), nir)
        self.assertIn(Point_d(2, [FT(n) for n in [-4, 0]]), nir)
        self.assertIn(Point_d(2, [FT(n) for n in [1, 0]]), nir)
        self.assertNotIn(Point_d(2, [FT(n) for n in [-40, 0]]), nir)



    def test_nn_cache(self):
        """
        Test nearest neighbors cache
        """
        k = 3
        radius = FT(5)
        points = [
            Point_d(2, [FT(n) for n in [4, 0]]),
            Point_d(2, [FT(n) for n in [-4, 0]]),
            Point_d(2, [FT(n) for n in [40, 0]]),
            Point_d(2, [FT(n) for n in [-40, 0]]),
            Point_d(2, [FT(n) for n in [1, 0]])]
        query = Point_d(2, [FT(n) for n in [0, 0]])
        nn = NearestNeighborsCached(NearestNeighbors_sklearn(Metric_Euclidean), max_cache=2)
        for point in points:
            nn.add_point(point)
        self.assertEqual(len(nn.nn.points), 4)
        self.assertEqual(len(nn.cache), 1)

        # Test knn
        knn = nn.k_nearest(query, k)
        self.assertEqual(len(knn), k)
        self.assertIn(Point_d(2, [FT(n) for n in [4, 0]]), knn)
        self.assertIn(Point_d(2, [FT(n) for n in [-4, 0]]), knn)
        self.assertIn(Point_d(2, [FT(n) for n in [1, 0]]), knn)
        self.assertNotIn(Point_d(2, [FT(n) for n in [-40, 0]]), knn)

        # Test nearest in radius (=nir)
        nir = nn.nearest_in_radius(query, radius)
        self.assertEqual(len(knn), 3)
        self.assertIn(Point_d(2, [FT(n) for n in [4, 0]]), nir)
        self.assertIn(Point_d(2, [FT(n) for n in [-4, 0]]), nir)
        self.assertIn(Point_d(2, [FT(n) for n in [1, 0]]), nir)
        self.assertNotIn(Point_d(2, [FT(n) for n in [-40, 0]]), nir)



if __name__ == "__main__":
    unittest.main()
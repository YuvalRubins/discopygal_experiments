import sys
import json
import math
import unittest
import pytest

sys.path.append('src')

from discopygal.bindings import *
from discopygal.solvers_infra import *
from discopygal.geometry_utils.transform import *
from discopygal.geometry_utils.display_arrangement import display_arrangement
import discopygal.geometry_utils.collision_detection as cd

TEST_CD_SCENE = './examples/scenes/test_collision_detection.json'

class TestCollisionDetection(unittest.TestCase):

    def test_collide_disc_with_polygon(self):
        center = Point_2(FT(0), FT(0))
        radius = FT(1)
        poly = Polygon_2([
            Point_2(FT(-1), FT(0)), Point_2(FT(0), FT(1)), Point_2(FT(1), FT(0)), Point_2(FT(0), FT(-1))
        ])
        self.assertTrue(cd.collide_disc_with_polygon(center, radius, poly)) # Interiors intersecting
        self.assertTrue(cd.collide_disc_with_polygon(center, radius, offset_polygon(poly, Point_2(FT(2), FT(0))))) # Intersecting at one point
        self.assertFalse(cd.collide_disc_with_polygon(center, radius, offset_polygon(poly, Point_2(FT(3), FT(0))))) # Disjoint
    
    def test_collide_disc_with_disc(self):
        self.assertTrue(cd.collide_disc_with_disc(Point_2(FT(0), FT(0)), FT(2), Point_2(FT(0), FT(0)), FT(1))) # Contained
        self.assertTrue(cd.collide_disc_with_disc(Point_2(FT(0), FT(0)), FT(2), Point_2(FT(2), FT(0)), FT(1))) # Interiors intersecting
        self.assertTrue(cd.collide_disc_with_disc(Point_2(FT(0), FT(0)), FT(2), Point_2(FT(3), FT(0)), FT(1))) # Intersecting at one point
        self.assertFalse(cd.collide_disc_with_disc(Point_2(FT(0), FT(0)), FT(2), Point_2(FT(4), FT(0)), FT(1))) # Disjoint

    def test_collide_disc_with_rod(self):
        center = Point_2(FT(0), FT(0))
        radius = FT(1)
        a = FT(30 / 180 * math.pi)
        length = FT(2)
        self.assertTrue(cd.collide_disc_with_rod(center, radius, FT(0), FT(0), a, length)) # Intersiors intersecting
        self.assertTrue(cd.collide_disc_with_rod(center, radius, FT(1), FT(0), a, length)) # Intersecting at one point
        self.assertFalse(cd.collide_disc_with_rod(center, radius, FT(2), FT(0), a, length)) # Disjoint

    def test_collision_detection_disc_robot(self):
        """
        Test ObjectCollisionDetection for a disc robot against a cluttered room  
        """
        # Load scene
        scene = Scene.from_file(TEST_CD_SCENE)

        # Find the correct robot
        robot = None
        for r in scene.robots:
            if type(r) is RobotDisc:
                robot = r
        self.assertIsNotNone(robot)

        # Build the collision detector
        obj_cd = cd.ObjectCollisionDetection(scene.obstacles, robot)
        
        # Test is_point_valid
        valid_points = [
            Point_2(FT(0), FT(1)), # Touching boundary
            Point_2(FT(2), FT(-1)), # Touching two boundaries
            Point_2(FT(6), FT(3)) # Totaly free
        ]
        invalid_points = [
            Point_2(FT(1), FT(0)),
            Point_2(FT(0), FT(5)),
            Point_2(FT(1), FT(7)),
        ]
        for point in valid_points:
            self.assertTrue(obj_cd.is_point_valid(point))
        for point in invalid_points:
            self.assertFalse(obj_cd.is_point_valid(point))

        # Test is_edge_valid
        self.assertTrue(obj_cd.is_edge_valid(Segment_2(
            Point_2(FT(-6), FT(1)), Point_2(FT(6), FT(1)) # Touches obstacle vertices
        )))
        self.assertTrue(obj_cd.is_edge_valid(Segment_2(
            Point_2(FT(-6), FT(-6)), Point_2(FT(6), FT(-6)) # Touches obstacle edges
        )))
        self.assertTrue(obj_cd.is_edge_valid(Segment_2(
            Point_2(FT(-6), FT(2)), Point_2(FT(6), FT(2)) # Totaly free
        )))
        self.assertFalse(obj_cd.is_edge_valid(Segment_2(
            Point_2(FT(-6), FT(-2)), Point_2(FT(6), FT(-2)) # Intersects
        )))
    
    def test_collision_detection_polygonal_robot(self):
        """
        Test ObjectCollisionDetection for a polygonal robot against a cluttered room  
        """
        # Load scene
        scene = Scene.from_file(TEST_CD_SCENE)

        # Find the correct robot
        robot = None
        for r in scene.robots:
            if type(r) is RobotPolygon:
                robot = r
        self.assertIsNotNone(robot)

        # Build the collision detector
        obj_cd = cd.ObjectCollisionDetection(scene.obstacles, robot)
        
        # Test is_point_valid
        valid_points = [
            Point_2(FT(0), FT(1)), # Touching boundary
            Point_2(FT(2), FT(-1)), # Touching two boundaries
            Point_2(FT(6), FT(3)), # Totaly free
            Point_2(FT(0), FT(5)), # Edges contained in boundary
        ]
        invalid_points = [
            Point_2(FT(1), FT(0)),
            Point_2(FT(0), FT(5.0001)),
            Point_2(FT(1), FT(7)),
        ]
        for point in valid_points:
            self.assertTrue(obj_cd.is_point_valid(point))
        for point in invalid_points:
            self.assertFalse(obj_cd.is_point_valid(point))

        # Test is_edge_valid
        self.assertTrue(obj_cd.is_edge_valid(Segment_2(
            Point_2(FT(-6), FT(1)), Point_2(FT(6), FT(1)) # Touches obstacle vertices
        )))
        self.assertTrue(obj_cd.is_edge_valid(Segment_2(
            Point_2(FT(-6), FT(-6)), Point_2(FT(6), FT(-6)) # Touches obstacle edges
        )))
        self.assertTrue(obj_cd.is_edge_valid(Segment_2(
            Point_2(FT(-6), FT(2)), Point_2(FT(6), FT(2)) # Totaly free
        )))
        self.assertFalse(obj_cd.is_edge_valid(Segment_2(
            Point_2(FT(-6), FT(-2)), Point_2(FT(6), FT(-2)) # Intersects
        )))
    
    def test_collide_two_robots(self):
        """
        Test collision between two robots
        """
        # start and end are non relevant for this test and are set to origin
        disc_robot = RobotDisc(FT(1), Point_2(FT(0), FT(0)), Point_2(FT(0), FT(0)))
        poly_robot = RobotPolygon(Polygon_2([
            Point_2(FT(-1), FT(0)), Point_2(FT(0), FT(1)), Point_2(FT(1), FT(0)), Point_2(FT(0), FT(-1))
        ]), Point_2(FT(0), FT(0)), Point_2(FT(0), FT(0)))

        # Disc vs Disc
        self.assertFalse(cd.collide_two_robots(
            disc_robot, Segment_2(Point_2(FT(0), FT(-3)), Point_2(FT(1), FT(3))),
            disc_robot, Segment_2(Point_2(FT(-4), FT(-3)), Point_2(FT(-4), FT(3))),
        ))
        self.assertFalse(cd.collide_two_robots(
            disc_robot, Segment_2(Point_2(FT(0), FT(-3)), Point_2(FT(0), FT(3))),
            disc_robot, Segment_2(Point_2(FT(-2), FT(-3)), Point_2(FT(-2), FT(3))),
        ))
        self.assertTrue(cd.collide_two_robots(
            disc_robot, Segment_2(Point_2(FT(0), FT(-3)), Point_2(FT(0), FT(3))),
            disc_robot, Segment_2(Point_2(FT(-1), FT(-3)), Point_2(FT(-1), FT(3))),
        ))
        self.assertTrue(cd.collide_two_robots(
            disc_robot, Segment_2(Point_2(FT(0), FT(-3)), Point_2(FT(-1), FT(3))),
            disc_robot, Segment_2(Point_2(FT(-1), FT(-3)), Point_2(FT(-1), FT(3))),
        ))

        # Polygon vs Polygon
        self.assertFalse(cd.collide_two_robots(
            poly_robot, Segment_2(Point_2(FT(0), FT(-3)), Point_2(FT(1), FT(3))),
            poly_robot, Segment_2(Point_2(FT(-4), FT(-3)), Point_2(FT(-4), FT(3))),
        ))
        self.assertFalse(cd.collide_two_robots(
            poly_robot, Segment_2(Point_2(FT(0), FT(-3)), Point_2(FT(0), FT(3))),
            poly_robot, Segment_2(Point_2(FT(-2), FT(-3)), Point_2(FT(-2), FT(3))),
        ))
        self.assertTrue(cd.collide_two_robots(
            poly_robot, Segment_2(Point_2(FT(0), FT(-3)), Point_2(FT(0), FT(3))),
            poly_robot, Segment_2(Point_2(FT(-1), FT(-3)), Point_2(FT(-1), FT(3))),
        ))
        self.assertTrue(cd.collide_two_robots(
            poly_robot, Segment_2(Point_2(FT(0), FT(-3)), Point_2(FT(-1), FT(3))),
            poly_robot, Segment_2(Point_2(FT(-1), FT(-3)), Point_2(FT(-1), FT(3))),
        ))

        # Polygon vs Disc
        self.assertFalse(cd.collide_two_robots(
            poly_robot, Segment_2(Point_2(FT(0), FT(-3)), Point_2(FT(1), FT(3))),
            disc_robot, Segment_2(Point_2(FT(-4), FT(-3)), Point_2(FT(-4), FT(3))),
        ))
        self.assertFalse(cd.collide_two_robots(
            poly_robot, Segment_2(Point_2(FT(0), FT(-3)), Point_2(FT(0), FT(3))),
            disc_robot, Segment_2(Point_2(FT(-2), FT(-3)), Point_2(FT(-2), FT(3))),
        ))
        self.assertTrue(cd.collide_two_robots(
            poly_robot, Segment_2(Point_2(FT(0), FT(-3)), Point_2(FT(0), FT(3))),
            disc_robot, Segment_2(Point_2(FT(-1), FT(-3)), Point_2(FT(-1), FT(3))),
        ))
        self.assertTrue(cd.collide_two_robots(
            poly_robot, Segment_2(Point_2(FT(0), FT(-3)), Point_2(FT(-1), FT(3))),
            disc_robot, Segment_2(Point_2(FT(-1), FT(-3)), Point_2(FT(-1), FT(3))),
        ))

        # Disc vs Polygon
        self.assertFalse(cd.collide_two_robots(
            disc_robot, Segment_2(Point_2(FT(0), FT(-3)), Point_2(FT(1), FT(3))),
            poly_robot, Segment_2(Point_2(FT(-4), FT(-3)), Point_2(FT(-4), FT(3))),
        ))
        self.assertFalse(cd.collide_two_robots(
            disc_robot, Segment_2(Point_2(FT(0), FT(-3)), Point_2(FT(0), FT(3))),
            poly_robot, Segment_2(Point_2(FT(-2), FT(-3)), Point_2(FT(-2), FT(3))),
        ))
        self.assertTrue(cd.collide_two_robots(
            disc_robot, Segment_2(Point_2(FT(0), FT(-3)), Point_2(FT(0), FT(3))),
            poly_robot, Segment_2(Point_2(FT(-1), FT(-3)), Point_2(FT(-1), FT(3))),
        ))
        self.assertTrue(cd.collide_two_robots(
            disc_robot, Segment_2(Point_2(FT(0), FT(-3)), Point_2(FT(-1), FT(3))),
            poly_robot, Segment_2(Point_2(FT(-1), FT(-3)), Point_2(FT(-1), FT(3))),
        ))




    

if __name__ == "__main__":
    unittest.main()
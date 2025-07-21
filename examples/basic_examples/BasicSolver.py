from discopygal.solvers_infra.Solver import Solver
from discopygal.solvers_infra import PathCollection, RobotRod, Path, PathPoint


class BasicSolver(Solver):
    """
    A basic solver example which it's solution paths are just a straight line from start point to end point
    (which is usually not valid).

    It has no arguments and doesn't use a bounding box.
    Doesn't do any special pre-processing when loading a scene (only the default :func:`load_scene` is invoked)
    """
    def __init__(self):
        # Don't set bounding box
        super().__init__(bounding_margin_width_factor=Solver.NO_BOUNDING_BOX)

    def _solve(self):
        """
        The base solver returns for each robot a simple path of its start and end position -
        which for most scenes might not be valid!

        :return: path collection of motion planning
        :rtype: :class:`~discopygal.solvers_infra.PathCollection`
        """
        path_collection = PathCollection()
        for robot in self.scene.robots:
            if type(robot) is RobotRod:
                start_location = robot.start[0]
                start_data = {'angle': robot.start[1]}
                end_location = robot.end[0]
                end_data = {'angle': robot.end[1]}
            else:
                start_location = robot.start
                start_data = {}
                end_location = robot.end
                end_data = {}
            start_point = PathPoint(start_location, start_data)
            end_point = PathPoint(end_location, end_data)
            path = Path([start_point, end_point])
            path_collection.add_robot_path(robot, path)
        return path_collection

    @classmethod
    def get_arguments(cls):
        return {}

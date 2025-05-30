import sys
import time
import numpy as np
from functools import partial
import pandas as pd

from discopygal.bindings import Point_2, FT
from discopygal.solvers_infra import Path, PathCollection, RobotDisc, Scene
from discopygal.solvers.bottleneck_tree.frechet_matching import FrechetMatching
from discopygal.solvers_infra.metrics import Metric_Euclidean
from discopygal.gui.color import PREDEFINED_COLORS
from discopygal_tools.solver_viewer import start_gui
from compare_frechets import get_curve, print_mem_usage


REPETITIONS = 10


class CustomFrechetPaths(FrechetMatching):
    def __init__(self, robots, paths, **kwargs):
        self.robots = robots
        self.paths = paths
        super().__init__(**kwargs)

    def generate_original_paths(self):
        paths = [Path.path_from_points([Point_2(path[i, 0], path[i, 1]) for i in range(path.shape[0])]) for path in self.paths]
        return PathCollection(dict(zip(self.robots, paths)))

    @staticmethod
    def solve_frechet_for_paths(paths, **kwargs):
        starts = [Point_2(path[0, 0], path[0, 1]) for path in paths]
        ends = [Point_2(path[-1, 0], path[-1, 1]) for path in paths]
        radius = min([1] + [Metric_Euclidean.dist(start, end) / 20 for start, end in zip(starts, ends)])
        robots = [RobotDisc(FT(radius), start, end, data={'color': list(PREDEFINED_COLORS.keys())[i+2]}) for i, (start, end) in enumerate(zip(starts, ends))]
        scene = Scene([], robots)
        solver = CustomFrechetPaths.init_solver(robots=robots, paths=paths, verbose=True, **kwargs)

        # start_gui(scene, solver)
        start_time = time.perf_counter()
        path_collection = solver.solve(scene)
        calc_time = time.perf_counter() - start_time

        if path_collection.is_empty():
            return float("NaN")

        return solver.calc_frechet_distance(path_collection)[2], calc_time

FACTOR = 15
PATHS = [get_curve(0, 0), get_curve(0, 1), np.array([[-16, 0], [16, 0]], dtype=np.float64),
         FACTOR * get_curve(3, 0), FACTOR * get_curve(3, 1), FACTOR * get_curve(10, 0), FACTOR * get_curve(10, 1),
         FACTOR * get_curve(15, 0), FACTOR * get_curve(15, 1), FACTOR * get_curve(13, 0), FACTOR * get_curve(13, 1)]
LANDMARKS_PER_NUM = {2: 100, 3: 200, 4: 300, 5: 750, 6: 3000, 7: 7_000, 8: 8_000, 9: 15_000, 10: 30_000}
RADIUS_PER_NUM = {2: 0.5, 3: 0.5, 4: 0.5, 5: 0.5, 6: 0.7, 7: 0.7, 8: 0.7, 9: 0.75, 10: 0.9}


def get_paths(number_of_paths):
    return PATHS[:number_of_paths]


def main():
    results = pd.DataFrame(columns=["Number of robots", "Method", "Frechet distance (avg)", "calc time (s) (avg)", "Frechet distance (std)", "calc time (s) (std)"])
    for num_of_robots in [int(sys.argv[1])]:
        landmarks = LANDMARKS_PER_NUM[num_of_robots]
        radius = RADIUS_PER_NUM[num_of_robots]
        func_name = f"Bottleneck Tree (landmarks={landmarks}, radius={radius})"
        func = partial(CustomFrechetPaths.solve_frechet_for_paths, num_landmarks_in_parameter_space=landmarks, radius=radius)
        print(f"\n**************** {num_of_robots=} ********************")
        case_results = pd.DataFrame(columns=["frechet_dist", "calc_time"])
        for _ in range(REPETITIONS):
            case_results.loc[len(case_results)] = func(get_paths(num_of_robots))
            print(case_results)
            print_mem_usage()
        case_results = case_results.astype("float").dropna()
        if len(case_results) == 0:
            result = (func_name, float("NaN"), float("NaN"), float("NaN"), float("NaN"))
        else:
            result = (func_name, *case_results.mean(), *case_results.std())

        print("{} -  Frechet dist: {}, calc time (s): {}".format(*result), flush=True)
        results.loc[len(results)] = (num_of_robots,) + result

    results.to_csv("multi_robot_frechet_comparison.csv", index=False)


if __name__ == "__main__":
    main()

import os
import re
import subprocess
import time
import numpy as np
import itertools as it
import urllib3
from functools import partial
import pandas as pd
import psutil
import threading
import sys
import multiprocessing
import dill

from frechetlib.continuous_frechet import frechet_c_approx
import frechetlib.frechet_utils as fu

from discopygal.bindings import Point_2, FT
from discopygal.solvers_infra import Path, PathCollection, RobotDisc, Scene
from discopygal.solvers.bottleneck_tree.frechet_matching import FrechetMatching
from discopygal.solvers_infra.metrics import Metric_Euclidean
from discopygal_tools.solver_viewer import start_gui


REPETITIONS = 5


def get_curve_file(curve_file):
    base_url = "https://sarielhp.org/p/24/frechet_ve/examples"
    curve_url = f"{base_url}/{curve_file}"
    print(curve_url)
    contents = urllib3.request("get", curve_url).data.decode("utf-8")

    lines = contents.split("\n")[:-1]
    x_coords = [float(line.split(',')[0]) for line in lines]
    y_coords = [-1 * float(line.split(',')[1]) for line in lines]

    assert len(x_coords) == len(y_coords)

    num_points = len(x_coords)

    output_curve: fu.Curve = np.ndarray(shape=(num_points, 2), dtype=np.float64)

    for i, x_coord, y_coord in zip(it.count(0), x_coords, y_coords):
        output_curve[i][0] = x_coord
        output_curve[i][1] = y_coord

    return output_curve


def alternating_heights_curves():
    alternating_heights_x = [-16]
    for x in range(-14, 15, 2):
        alternating_heights_x += [x] * 2
    alternating_heights_x += [16]

    alternating_heights_y = [3, 3]
    for i in range(14):
        alternating_heights_y += [10 if i % 2 == 0 else -10] * 2
    alternating_heights_y += [-3, -3]
    alternating_heights_x = np.array(alternating_heights_x)
    alternating_heights_y = np.array(alternating_heights_y)
    curve_1 = np.array([alternating_heights_x, alternating_heights_y], dtype=np.float64).T
    curve_2 = np.array([alternating_heights_x, -1 * alternating_heights_y], dtype=np.float64).T
    return curve_1, curve_2


def get_curve(curve_number, robot_number):
    if curve_number == 0:
        return alternating_heights_curves()[robot_number]
    else:
        return get_curve_file(f"{str(curve_number).rjust(2, '0')}/poly_{'a' if robot_number == 0 else 'b'}.txt")


def run_frechetlib_har_peled(path1, path2):
    # Sariel Har-Peled
    # print("=========================== External Frechet =======================")
    # NOTE Run twice to factor out the compilation time from the timing.
    # frechet_c_approx(path1, path2, 1.01)

    res, morphing = frechet_c_approx(path1, path2, 1.01)

    return morphing.dist


def run_freceht_bringmann(path1, path2):
    with open("path1.txt", "w") as f:
        f.writelines([f"{path1[i][0]} {path1[i][1]}\n" for i in range(path1.shape[0])])
    with open("path2.txt", "w") as f:
        f.writelines([f"{path2[i][0]} {path2[i][1]}\n" for i in range(path2.shape[0])])

    output = subprocess.check_output(["./bringmann_calc_frechet_distance", "path1.txt", "path2.txt"])
    frechet_dist = float(re.search(b": (\d+\.\d*)", output).group(1))

    os.remove("path1.txt")
    os.remove("path2.txt")
    return frechet_dist


class CustomFrechetPaths(FrechetMatching):
    def __init__(self, robots, paths, **kwargs):
        self.robots = robots
        self.paths = paths
        super().__init__(**kwargs)

    def generate_original_paths(self):
        robot1, robot2 = self.robots
        path1, path2 = self.paths
        path1 = Path.path_from_points([Point_2(path1[i, 0], path1[i, 1]) for i in range(path1.shape[0])])
        path2 = Path.path_from_points([Point_2(path2[i, 0], path2[i, 1]) for i in range(path2.shape[0])])
        return PathCollection({robot1: path1, robot2: path2})

    @staticmethod
    def solve_frechet_for_paths(path1, path2, **kwargs):
        # print("=========================== Our Frechet =======================")
        start1 = Point_2(path1[0, 0], path1[0, 1])
        end1 = Point_2(path1[-1, 0], path1[-1, 1])
        start2 = Point_2(path2[0, 0], path2[0, 1])
        end2 = Point_2(path2[-1, 0], path2[-1, 1])
        radius = min([1, Metric_Euclidean.dist(start1, end1) / 20, Metric_Euclidean.dist(start2, end2) / 20,
                         Metric_Euclidean.dist(start1, start2) / 2, Metric_Euclidean.dist(end1, end2) / 2])
        robot1 = RobotDisc(FT(radius), start1, end1, data={'color': 'red'})
        robot2 = RobotDisc(FT(radius), start2, end2, data={'color': 'blue'})
        scene = Scene([], [robot1, robot2])
        solver = CustomFrechetPaths.init_solver(robots=[robot1, robot2], paths=[path1, path2], verbose=False, **kwargs)

        # start_gui(scene, solver)
        path_collection = solver.solve(scene)

        if path_collection.is_empty():
            return float("NaN")

        return solver.calc_frechet_distance(path_collection)[2]


FUNCTIONS = {
            #  "Har Peled": run_frechetlib_har_peled,
            #  "Bringmann": run_freceht_bringmann,
            #  "Bottleneck Tree (landmarks=50, radius=0.25)": partial(CustomFrechetPaths.solve_frechet_for_paths, num_landmarks_in_parameter_space=50, radius=0.25),
            #  "Bottleneck Tree (landmarks=75, radius=0.25)": partial(CustomFrechetPaths.solve_frechet_for_paths, num_landmarks_in_parameter_space=75, radius=0.25),
            #  "Bottleneck Tree (landmarks=100, radius=0.25)": partial(CustomFrechetPaths.solve_frechet_for_paths, num_landmarks_in_parameter_space=100, radius=0.25),
            #  "Bottleneck Tree (landmarks=50, radius=0.5)": partial(CustomFrechetPaths.solve_frechet_for_paths, num_landmarks_in_parameter_space=50, radius=0.5),
             "Bottleneck Tree (landmarks=200, radius=0.1)": partial(CustomFrechetPaths.solve_frechet_for_paths, num_landmarks_in_parameter_space=200, radius=0.5),
            #  "Bottleneck Tree (landmarks=200, radius=0.5)": partial(CustomFrechetPaths.solve_frechet_for_paths, num_landmarks_in_parameter_space=200, radius=0.5),
            #  "Bottleneck Tree (landmarks=1000, radius=0.5)": partial(CustomFrechetPaths.solve_frechet_for_paths, num_landmarks_in_parameter_space=1000, radius=0.5),
            #  "Bottleneck Tree (landmarks=2000, radius=0.25)": partial(CustomFrechetPaths.solve_frechet_for_paths, num_landmarks_in_parameter_space=2000, radius=0.25)
            }


def run_func(func, curve_1, curve_2, return_values: list):
    start_time = time.perf_counter()
    frechet_dist = func(curve_1, curve_2)
    calc_time = time.perf_counter() - start_time
    return_values.extend([frechet_dist, calc_time])


def print_mem_usage():
    memory_info = psutil.virtual_memory()
    print(f"Memory Usage: {memory_info.percent}% ({memory_info.used / (1024 ** 2):.2f} MB used)", flush=True)


def run_func_process(input_queue: multiprocessing.Queue, output_queue: multiprocessing.Queue):
    func = input_queue.get()
    args = input_queue.get()
    results = []
    run_func(func, *args, results)
    results[0] = float(results[0])
    output_queue.put(results)
    output_queue.close()
    output_queue.join_thread()


def create_run_func_process(run_func, *args):
    input_queue = multiprocessing.Queue()
    output_queue = multiprocessing.Queue()
    input_queue.put(run_func)
    input_queue.put(args)
    process = multiprocessing.Process(target=run_func_process, args=(input_queue, output_queue))
    process.start()
    process.join()
    results = output_queue.get(block=False)
    return results


def main():
    try:
        scenes_to_run = {int(sys.argv[1])}
    except IndexError:
        scenes_to_run = set(range(0, 16)).difference({11})

    did_init_har_peled = False
    results = pd.DataFrame(columns=["Curve number", "Method", "Frechet distance (avg)", "calc time (s) (avg)", "Frechet distance (std)", "calc time (s) (std)"])
    for curve_index in scenes_to_run:
        print(f"\n**************** Curve {curve_index} ********************")
        big_curve_1 = get_curve(curve_index, 0)
        big_curve_2 = get_curve(curve_index, 1)
        if not did_init_har_peled:
            run_frechetlib_har_peled(big_curve_1, big_curve_2)
            did_init_har_peled = True

        for func_name, func in FUNCTIONS.items():
            print_mem_usage()
            case_results = pd.DataFrame(columns=["frechet_dist", "calc_time"])
            for _ in range(REPETITIONS):
                case_results.loc[len(case_results)] = create_run_func_process(func, big_curve_1, big_curve_2)
                print(case_results)
            case_results = case_results.astype("float").dropna()
            if len(case_results) == 0:
                result = (func_name, float("NaN"), float("NaN"), float("NaN"), float("NaN"))
            else:
                result = (func_name, *case_results.mean(), *case_results.std())

            print("{} -  Frechet dist: {}, calc time (s): {}".format(*result), flush=True)
            results.loc[len(results)] = (curve_index,) + result
        # print(results.tail(len(FUNCTIONS)))

    results.to_csv("frechet_comparison.csv", index=False)


if __name__ == "__main__":
    main()

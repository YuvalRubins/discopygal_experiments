import importlib
import time
import pytest
from inspect import isclass

from discopygal.solvers_infra import Scene
from discopygal.solvers_infra.verify_paths import verify_paths
from examples.basic_examples.RandomSolver import RandomSolver
from discopygal.solvers import get_solver_class, get_available_solvers, import_default_solvers


import_default_solvers()
ALL_SOLVERS = set(get_available_solvers())
BASIC_SCENE = 'examples/basic_examples/basic_scene.json'
has_ra = ("RevlovingAreas" in ALL_SOLVERS)


def solve_scene(solver, scene_path):
    start_time = time.time()
    scene = Scene.from_file(scene_path)
    if isinstance(solver, str):
        solver = get_solver_class(solver)
    if isclass(solver):
        solver = solver.init_default_solver()
    solver.set_verbose()
    path_collection = solver.solve(scene)
    result, reason = verify_paths(scene, path_collection)
    print(f"Are paths valid: {result}\t{reason}")
    print(f"Time took: {time.time() - start_time}")
    return result, reason, path_collection


def check_solved_scene(solver, scene_path):
    result, reason, path_collection = solve_scene(solver, scene_path)
    assert path_collection is not None
    assert result
    assert reason == ""
    return path_collection


@pytest.mark.parametrize("solver_class",
                         ALL_SOLVERS.difference({"HGraph_PRM", "HGraph_RRT", "PRM2", "PRM3", "BasicRodPRM", "FrechetMatching"}))
def test_single_disc_solver(solver_class):
    check_solved_scene(solver_class, BASIC_SCENE)


@pytest.mark.parametrize("scene_path", ['examples/basic_examples/simple_motion_planning_scene.json', "examples/scenes/2_discs_corridor.json"])
@pytest.mark.parametrize("solver_class",
                         ALL_SOLVERS.difference({"HGraph_PRM", "HGraph_RRT", "ExactSingle", "BasicRodPRM", "RevolvingAreas", "FrechetMatching"}))
def test_multiple_disc_solver(solver_class, scene_path):
    if isinstance(solver_class, str):
        solver_class = get_solver_class(solver_class)
    solver = solver_class.init_solver(bounding_margin_width_factor=0)
    check_solved_scene(solver, scene_path)


def test_multiple_loads():
    solver = get_solver_class("PRM").init_default_solver()
    scene = Scene.from_file(BASIC_SCENE)
    solver.load_scene(scene)
    assert solver.solve() is not None
    assert solver.solve() is not None
    assert solver.solve(scene) is not None


def test_random_solver():
    result, reason, path_collection = solve_scene(RandomSolver, BASIC_SCENE)
    assert path_collection is not None
    assert not result
    assert reason.startswith("Collision with obstacle") or reason == "Empty path"


@pytest.mark.parametrize("scene_file", ["coffee_shop.json", "coffee_shop_two_discs.json"])
def test_coffee_shop(scene_file):
    check_solved_scene(get_solver_class("PRM"), "examples/scenes/coffee_shop/" + scene_file)


@pytest.mark.parametrize("scene_path", ["examples/scenes/square_scene.json",
                                        "examples/scenes/test_swap.json"])
def test_staggered_grid(scene_path):
    solver = get_solver_class("StaggeredGrid").init_solver(eps=9999, delta=0.03)
    check_solved_scene(solver, scene_path)


@pytest.mark.parametrize("scene_path", ["examples/scenes/legacy/3_circular_room_disc.json",
                                        "examples/scenes/square_scene.json"])
def test_drrt_staggered_grid(scene_path):
    check_solved_scene(get_solver_class("dRRTStaggeredGrid").init_solver(eps=9999, delta=0.03, num_landmarks=1000, k_nn=15), scene_path)

@pytest.mark.parametrize("scene_path", ["examples/scenes/legacy/3_circular_room_disc.json",
                                        "examples/scenes/square_scene.json"])
def test_min_staggered_grid(scene_path):
    check_solved_scene(get_solver_class("StaggeredGridMinPath").init_solver(eps=9999, delta=0.03, num_landmarks=1000, k_nn=15), scene_path)


@pytest.mark.skip
def test_hard_drrt_staggered_grid():
    check_solved_scene(get_solver_class("dRRTStaggeredGrid").init_solver(eps=9999, delta=0.03, num_landmarks=1000, k_nn=15), "examples/scenes/test_swap.json")


@pytest.mark.skip
def test_swap_staggered_grid():
    check_solved_scene(get_solver_class("StaggeredGrid").init_solver(eps=9999, delta=0.03), "examples/scenes/test_swap.json")


@pytest.mark.parametrize("scene_file", ["1_rod_example.json", "2_rod_example.json", "3_rod_maze.json",
                                        "rod_1.json", "rod_2.json", "simple_rod.json"])
def test_prm_rod(scene_file):
    solver = get_solver_class("BasicRodPRM").init_solver(bounding_margin_width_factor=0, num_landmarks=2000)
    check_solved_scene(solver, "examples/scenes/" + scene_file)


@pytest.mark.parametrize("scene_file", ["1_narrow_gate_square.json", "1_narrow_gate_poly3.json", "spiral.json",
                                        "tunnels_disc.json"]) # "coffee_shop\coffee_shop2.json"
def test_exact_single(scene_file):
    check_solved_scene(get_solver_class("ExactSingle"), "examples/scenes/" + scene_file)


@pytest.mark.parametrize("scene_file", ['2_pocket_maze_tight.json', '3_discs1.json', '2_discs_corridor.json'])
def test_drrt_star(scene_file):
    check_solved_scene(get_solver_class("dRRT_star"), f'examples/scenes/{scene_file}')


@pytest.mark.parametrize("solver_class", ["HGraph_PRM", "HGraph_RRT"])
@pytest.mark.parametrize("scene_file", ["examples/scenes/1_narrow_gate_poly3.json"])
def test_hgraphs(solver_class, scene_file):
    check_solved_scene(get_solver_class(solver_class).init_solver(num_path=5, neighborhood_distance=1), scene_file)


@pytest.mark.skipif(not has_ra, reason="Doesn't have RA")
@pytest.mark.parametrize("mode", ["revolving", "pairs"])
@pytest.mark.parametrize("scene_file", ["grid_20_sparse.json", "triangles_20_dense.json"])  # "grid_100_sparse.json"])
def test_revolving_areas_classic(scene_file, mode):
    check_solved_scene(get_solver_class("RevolvingAreas").init_solver(mode=mode), f'examples/scenes/revolving_areas/{scene_file}')

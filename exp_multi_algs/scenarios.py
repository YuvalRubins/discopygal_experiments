import numpy as np
from itertools import product

from discopygal.experiments.scenarios_runner import Scenario
from discopygal.solvers.prm.prm import PRM
from discopygal.solvers.rrt.rrt import RRT
from discopygal.solvers.rrt.rrt_star import RRT_star
from discopygal.solvers.rrt.drrt import dRRT
from discopygal.solvers.rrt.drrt_star import dRRT_star
from discopygal.solvers.staggered_grid import StaggeredGrid
from discopygal.solvers.rrt.lbt_rrt import LBT_RRT
from discopygal.solvers.rrt.birrt import BiRRT

budgets = range(100, 10_000 + 1, 100)

PRM_AVERAGE_EDGES_PER_NODE = 6
ALGOS = [PRM, RRT, RRT_star, dRRT, dRRT_star, LBT_RRT, BiRRT]
# ALGOS = [dRRT_star]


# def get_params(solver_class, budget):
#     return {
#         PRM: {"num_landmarks": budget // PRM_AVERAGE_EDGES_PER_NODE},                     # budget = num of edges
#         RRT: {"num_landmarks": budget},                                                   # budget = num of landmarks
#         RRT_star: {"num_landmarks": budget, 'radius': 5},                                 # budget = num of landmarks
#         dRRT: {"num_landmarks": budget // PRM_AVERAGE_EDGES_PER_NODE, "prm_num_landmarks": 4 * budget // PRM_AVERAGE_EDGES_PER_NODE},       # budget = num of prm edges + num_of_landmarks (ratio 1:4)
#         dRRT_star: {"num_landmarks": budget // (PRM_AVERAGE_EDGES_PER_NODE * 10), "prm_num_landmarks": 4 * budget // (PRM_AVERAGE_EDGES_PER_NODE * 10)}  # budget = num of prm edges + num_of_landmarks * num_of_expands
#         # dRRT: {"num_landmarks": budget // 4, "prm_num_landmarks": 3 * budget // PRM_AVERAGE_EDGES_PER_NODE},       # budget = num of prm edges + num_of_landmarks (ratio 1:4)
#         # dRRT_star: {"num_landmarks": budget // 40, "prm_num_landmarks": 3 * budget // 4}  # budget = num of prm edges + num_of_landmarks * num_of_expands
#     }[solver_class]


# def calc_budget(solver):
#     if solver.roadmap is None:
#         return float("Nan")
#     else:
#         return len(solver.roadmap.edges)
#     # elif isinstance(solver, (PRM, RRT, RRT_star)):
#     #     return len(solver.roadmap.edges)
#     # elif isinstance(solver, dRRT_star):
#     #     return solver.num_landmarks * solver.num_expands + sum([len(roadmap.edges) for roadmap in solver.tensor_roadmap.roadmaps.values()]) / len(solver.tensor_roadmap.robots)
#     # elif isinstance(solver, dRRT):
#     #     return solver.num_landmarks + sum([len(roadmap.edges) for roadmap in solver.tensor_roadmap.roadmaps.values()]) / len(solver.tensor_roadmap.robots)



# Budget == num of actions
def get_params(solver_class, budget):
    return {
        PRM: {"num_landmarks": budget},
        RRT: {"num_landmarks": budget},
        RRT_star: {"num_landmarks": budget, 'radius': 5},
        dRRT: {"num_landmarks": budget // 10, "prm_num_landmarks": 5 * budget // 10},
        dRRT_star: {"num_landmarks": budget // (10 * 10), "prm_num_landmarks": 5 * budget // (10 * 10)},
        LBT_RRT: {"num_landmarks": budget},
        BiRRT: {"num_landmarks": budget},
        # dRRT: {"num_landmarks": budget // 4, "prm_num_landmarks": 3 * budget // PRM_AVERAGE_EDGES_PER_NODE},       # budget = num of prm edges + num_of_landmarks (ratio 1:4)
        # dRRT_star: {"num_landmarks": budget // 40, "prm_num_landmarks": 3 * budget // 4}  # budget = num of prm edges + num_of_landmarks * num_of_expands
    }[solver_class]


def calc_budget(solver):
    return sum(solver.basic_operations_call_counts.values())
    # if solver.roadmap is None:
    #     return float("Nan")
    # else:
    #     return len(solver.roadmap.edges)
    # elif isinstance(solver, (PRM, RRT, RRT_star)):
    #     return len(solver.roadmap.edges)
    # elif isinstance(solver, dRRT_star):
    #     return solver.num_landmarks * solver.num_expands + sum([len(roadmap.edges) for roadmap in solver.tensor_roadmap.roadmaps.values()]) / len(solver.tensor_roadmap.robots)
    # elif isinstance(solver, dRRT):
    #     return solver.num_landmarks + sum([len(roadmap.edges) for roadmap in solver.tensor_roadmap.roadmaps.values()]) / len(solver.tensor_roadmap.robots)


def num_of_edges(solver):
    if solver.roadmap is None:
        return float("NaN")
    else:
        return len(solver.roadmap.edges)


def num_of_points(solver):
    if solver.roadmap is None:
        return float("NaN")
    else:
        return len(solver.roadmap.points)


scenes = [
          "scenes/legacy/2_monster_disc.json",
          "scenes/tunnels_disc.json",
          "scenes/coffee_shop/coffee_shop.json",
          "scenes/2_pocket_maze_tight.json",
          "scenes/2_discs_corridor.json",
          "scenes/legacy/3_glass_disc.json",
          "scenes/3_discs1.json",
          "scenes/vertical_clearance_maze_disc.json",
          "scenes/two_free_discs_symmetric.json",
          "scenes/two_free_discs3.json",
        ]


SCENARIOS = [Scenario(solver, scene, get_params(solver, budget))
             for solver, scene, budget in product(ALGOS, scenes, budgets)
             ] # + [Scenario(StaggeredGrid, scene, repetitions=1) for scene in scenes]


# RESULT_HANDLERS = {"budget": lambda _, solver: calc_budget(solver), "num_of_edges": lambda _, solver: num_of_edges(solver)}
RESULT_HANDLERS = {#"budget": lambda _, solver: calc_budget(solver),
                   "num_of_edges": lambda _, solver: num_of_edges(solver),
                   "num_of_nodes": lambda _, solver: num_of_points(solver),
                   "operations_count": lambda _, solver: str(solver.operations_counter.basic_operations_call_counts),
                   "mean_time_to_inc_operation_ratio": lambda _, solver: str({k: float(np.mean(solver.operations_counter.time_to_increment_ratios[k])) for k in solver.operations_counter.time_to_increment_ratios}),
                   "std_time_to_inc_operation_ratio": lambda _, solver: str({k: float(np.std(solver.operations_counter.time_to_increment_ratios[k])) for k in solver.operations_counter.time_to_increment_ratios})}

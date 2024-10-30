import sys
import itertools

from discopygal.experiments.scenarios_runner import run_scenarios, Scenario
from discopygal.solvers.rrt.drrt_star import dRRT_star
from discopygal.solvers.prm.prm import PRM

# num_of_landmarks = [100, 200, 300, 400, 500, 600, 700, 800, 900, 1000, 1200, 1400, 1600, 1800, 2000, 2200, 2400, 2600,
#                     2800, 3000, 3500, 4000, 4500, 5000, 5500, 6000, 6500, 7000, 7500, 8000, 8500, 9000, 9500, 10000]
# num_of_expands = [10, 20, 30, 40, 50, 60, 70, 80, 90, 100, 120, 140, 160, 180, 200, 250, 300, 350, 400, 450, 500, 550,
#                   600, 650, 700, 750, 800, 850, 900, 950, 1000, 1050, 1100, 1150, 1200, 1250, 1300, 1350, 1400, 1450,
#                   1500, 1550, 1600, 1650, 1700, 1750, 1800, 1850, 1900, 1950, 2000]
# NUM_OF_LANDMARKS = range(500, 10001, 500)
# NUM_OF_EXPANDS = range(50, 1001, 50)
# SCENE_PATH = "examples/scenes/2_pocket_maze_tight.json"
# SCENE_PATH = "examples/scenes/tunnels_disc.json"
# scenarios = [Scenario(dRRT_star, SCENE_PATH, {"random_sample_counter": 0}),
#              Scenario(dRRT_star, SCENE_PATH, {"prm_num_landmarks": 2000, "num_landmarks": 100, "random_sample_counter": 0})]
# extra_handlers = {"size_of_roadmap": lambda _, solver: len(solver.roadmap.edges),
#                   "num_of_nodes": lambda _, solver: len(solver.roadmap.points)}

random_sample_counter_list = [0, 1, 10, 20, 30, 50, 75, 100, 200, 500]

scenes = ["scenes/tunnels_disc.json",
          "scenes/coffee_shop/coffee_shop.json",
          "scenes/2_discs_corridor.json",
          "scenes/2_pocket_maze_tight.json",
          "scenes/legacy/2_monster_disc.json",
          "scenes/legacy/3_glass_disc.json",
          "scenes/3_discs1.json",
          "scenes/vertical_clearance_maze_disc.json",
          "scenes/two_free_discs_symmetric.json",
          "scenes/two_free_discs3.json"]


scenarios = [Scenario(dRRT_star, scene, {"prm_num_landmarks": 1000, "num_landmarks": 100, "random_sample_counter": random_sample_counter}) for
             random_sample_counter, scene in itertools.product(random_sample_counter_list, scenes)]

scenarios = [Scenario(dRRT_star, scene) for scene in scenes[:2]]

chunk = int(sys.argv[1])
print(f"{chunk=}")

run_scenarios([scenarios[chunk]], "results_drrt_star", resume_latest=True)

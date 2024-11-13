import os
import sys
import shutil
import random
import pandas as pd

from discopygal.experiments.run_experiment import load_scenarios_and_handlers
from discopygal.experiments.scenarios_runner import get_latest_dir, get_results_experiment_path

scenarios_file = sys.argv[1]
results_path = sys.argv[2]
scenarios, _ = load_scenarios_and_handlers(scenarios_file)

all_results_path = get_latest_dir(f"{results_path}/all")
all_ordered_results_path = get_results_experiment_path(f"{results_path}/all_ordered")
os.makedirs(all_ordered_results_path)
results_table = pd.read_csv(f"{all_results_path}/results.csv")
random.seed(0)
shuffled_index_to_original_index = list(range(len(results_table)))
random.shuffle(shuffled_index_to_original_index)

for scenario_result_file in os.listdir(all_results_path):
    if scenario_result_file.startswith("scenario_"):
        scenario_index = int(scenario_result_file.split('.')[0].split('_')[1])
        original_scenarios_index = shuffled_index_to_original_index[scenario_index]
        shutil.copy(f"{all_results_path}/{scenario_result_file}", f"{all_ordered_results_path}/scenario_{original_scenarios_index}.csv")

results_table["index_scenario"] = shuffled_index_to_original_index
results_table = results_table.sort_values("index_scenario")
results_table.to_csv(f"{all_ordered_results_path}/results.csv", index=False)
# shutil.rmtree(all_results_path)
# shutil.copytree(all_ordered_results_path, all_results_path)

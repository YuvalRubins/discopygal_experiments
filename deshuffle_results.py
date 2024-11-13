import os
import sys
import shutil
import pandas as pd

from discopygal.experiments.run_experiment import load_scenarios_and_handlers
from discopygal.experiments.scenarios_runner import get_latest_dir, get_results_experiment_path

scenarios_file = sys.argv[1]
results_path = sys.argv[2]
scenarios, _ = load_scenarios_and_handlers(scenarios_file)

all_results_path = get_latest_dir(f"{results_path}/all")
all_ordered_results_path = get_results_experiment_path(f"{results_path}/all_ordered")


def get_original_scenarios_index(scenario_index, results_table):
    scenario_entry = results_table.loc[scenario_index]
    return scenario_to_index[scenario_entry['solver_class'], scenario_entry['scene_path'], scenario_entry['parameters']]


results_table = pd.read_csv(f"{all_results_path}/results.csv")
all_ordered_results_path = pd.DataFrame(columns=results_table.columns)

scenario_to_index = {(scenario.solver_class.__name__, scenario.scene_path, str(scenario.parameters)): index for
                     index, scenario in enumerate(scenarios)}

shuffled_index_to_original_index = [get_original_scenarios_index(shuffled_index, results_table)
                                    for shuffled_index in range(len(results_table))]

for scenario_result_file in os.listdir(all_results_path):
    if scenario_result_file.startswith("scenario_"):
        scenario_index = int(scenario_result_file.split('.')[0].split('_')[1])
        original_scenarios_index = shuffled_index_to_original_index[scenario_index]
        shutil.copy(f"{all_results_path}/{scenario_result_file}", f"{all_ordered_results_path}/scenario_{original_scenarios_index}.csv")

print("hi")
results_table["index_scenario"] = shuffled_index_to_original_index
results_table.sort("index_scenario")
results_table.to_csv(f"{all_ordered_results_path}/results.csv", index=False)
# shutil.rmtree(all_results_path)
# shutil.copytree(all_ordered_results_path, all_results_path)

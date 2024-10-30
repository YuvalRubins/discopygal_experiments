import os
import sys
import shutil
import importlib
import pandas as pd
from datetime import datetime
from discopygal.experiments.scenarios_runner import run_scenarios


# Args: scenarios_file, number_of_chunks, chunk_number # To run chunk
# Args: scenarios_file, number_of_chunks, end          # To create final dir

RESULTS_DIR_PREFIX = "results__"
RESULTS_ROOT_DIR = "results"

scenarios_file = sys.argv[1]
number_of_chunks = int(sys.argv[2])

sys.path.append(os.path.dirname(scenarios_file))
scenarios_module_name = os.path.basename(scenarios_file).rstrip(".py")
scenarios_module = importlib.import_module(scenarios_module_name)
scenarios = getattr(scenarios_module, "SCENARIOS")
scenarios_per_chunk = int(len(scenarios) / number_of_chunks)


def get_latest_dir(root_dir):
    def check_format(name):
        if name.startswith(RESULTS_DIR_PREFIX):
            try:
                datetime.strptime(name[len(RESULTS_DIR_PREFIX):], '%d_%m_%y__%H_%M_%S')
                return True
            except ValueError:
                pass
        return False

    files_names = [f[len(RESULTS_DIR_PREFIX):] for f in os.listdir(root_dir) if check_format(f)]
    files_names.sort(key=lambda x: datetime.strptime(x, '%d_%m_%y__%H_%M_%S'), reverse=True)
    return f"{root_dir}/{RESULTS_DIR_PREFIX}{files_names[0]}"


if sys.argv[3] == "end":
    all_results_path = f"{RESULTS_ROOT_DIR}/all"
    chunk_dirs = os.listdir(RESULTS_ROOT_DIR)
    os.mkdir(all_results_path)

    results_per_chunk = []
    for f in chunk_dirs:
        assert f.startswith("chunk_")
        chunk_index = int(f.split('_')[1])
        chunk_dir = get_latest_dir(f"{RESULTS_ROOT_DIR}/{f}")
        print(f"Copying from {chunk_dir}")

        chunk_index_offset = scenarios_per_chunk * chunk_index
        chunk_results = pd.read_csv(f"{chunk_dir}/results.csv")
        chunk_results["scenario_index"] += chunk_index_offset
        results_per_chunk.append(chunk_results)
        for c in os.listdir(chunk_dir):
            if c.startswith("scenario_"):
                scenario_index = int(c.split('.')[0].split('_')[1])
                shutil.copy(f"{chunk_dir}/{c}", f"{all_results_path}/scenario_{chunk_index_offset + scenario_index}")

    all_results = pd.concat(results_per_chunk)
    all_results.sort_values(by=["scenario_index"])
    all_results.to_csv(f"{all_results_path}/results.csv", index=False)

    sys.exit()

chunk = int(sys.argv[3])
print(f"Running {chunk=}")

run_scenarios(scenarios[chunk * scenarios_per_chunk: (chunk+1) * scenarios_per_chunk], f"{RESULTS_ROOT_DIR}/chunk_{chunk}")

import os
import sys
import importlib
from discopygal.experiments.scenarios_runner import run_scenarios


# Args: scenarios_file, chunk_number, number_of_chunks # To run chunk
# Args: end                                            # To create final dir

if sys.argv[1] == "end":
    os.system("echo hello > results/end.txt")
    exit()

scenarios_file = sys.argv[1]
chunk = int(sys.argv[2])
number_of_chunks = int(sys.argv[3])

sys.path.append(os.path.dirname(scenarios_file))
scenarios_module_name = os.path.basename(scenarios_file).rstrip(".py")
scenarios_module = importlib.import_module(scenarios_module_name)
scenarios = getattr(scenarios_module, "SCENARIOS")
scenarios_per_chunk = int(len(scenarios) / number_of_chunks)


print(f"Running {chunk=}")

run_scenarios(scenarios[chunk * scenarios_per_chunk: (chunk+1) * scenarios_per_chunk], f"results/chunk_{chunk}")

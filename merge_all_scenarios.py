import sys
import os
import pandas as pd

scenarios_dir_path = sys.argv[1]
dfs = []

for scenario_file in os.listdir(scenarios_dir_path):
    if not scenario_file.startswith("scenario_"):
        continue

    scenario_index = int(scenario_file.split('.')[0].split('_')[1])
    df = pd.read_csv(f"{scenarios_dir_path}/{scenario_file}")
    df["scenario_index"] = scenario_index
    df["repetition"] = df["Unnamed: 0"]
    columns = list(df.columns)
    columns.remove("Unnamed: 0")
    columns.remove("scenario_index")
    columns.remove("repetition")
    df = df[["scenario_index", "repetition"] + columns]
    dfs.append(df)

all_scenarios_df = pd.concat(dfs)
all_scenarios_df = all_scenarios_df.sort_values(["scenario_index", "repetition"])
all_scenarios_df.to_csv(f"{scenarios_dir_path}/all_scenarios.csv", index=False)

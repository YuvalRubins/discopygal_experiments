import os
import pandas as pd
from functools import reduce

from scenarios import scenes


ALGOS = ["PRM", "RRT", "RRT_star", "dRRT", "dRRT_star"]


def get_filename(path):
    return os.path.basename(path).split('.')[0]


def get_Y_per_X(results_df, scene, solver_class, X, Y):
    a = results_df.loc[(results_df["scene_path"] == scene) &
                       (results_df["solver_class"] == solver_class), [X, Y]]
    a.index = a[X]
    a[solver_class] = a[Y]
    a = a.drop([X, Y], axis=1)
    return a


def get_Y_per_X_all_algos(results_df, scene, X, Y):
    return reduce(lambda df1, df2: pd.merge(df1, df2, left_index=True ,right_index=True, how="outer"),
                  [get_Y_per_X(results_df, scene, solver_class, X, Y)
                   for solver_class in ALGOS])


def get_lengths_per_budget_all_algos(results_df, scene):
    return get_Y_per_X_all_algos(results_df, scene, "budget_avg", "total_path_length_avg")


def get_lengths_per_calc_time_all_algos(results_df, scene):
    return get_Y_per_X_all_algos(results_df, scene, "calc_time_avg", "total_path_length_avg")


results_df = pd.read_csv("results.csv")
for scene in scenes:
    get_lengths_per_budget_all_algos(results_df, scene).to_csv(f"check_{get_filename(scene)}.csv")
    # get_lengths_per_calc_time_all_algos(results_df, scene).to_csv(f"check_{get_filename(scene)}.csv")

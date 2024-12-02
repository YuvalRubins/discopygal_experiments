import os
import sys
import pandas as pd
from functools import reduce
from openpyxl.chart import ScatterChart, Reference, Series

from scenarios import scenes, ALGOS

try:
    results_file_path = sys.argv[1]
except IndexError:
    print("Usage: python analyze_results.py <path_to_results_file>")


def get_filename(path):
    return os.path.basename(path).split('.')[0]


def remove_style_from_worksheet(worksheet):
    for row in worksheet.iter_rows():
        for cell in row:
            cell.style = 'Normal'


def get_Y_per_X(results_df, scene, solver_class, X, Y):
    a = results_df.loc[(results_df["scene_path"] == scene) &
                       (results_df["solver_class"] == solver_class), [X, Y]]
    a.index = a[X]
    a[solver_class] = a[Y]
    a = a.drop([X, Y], axis=1)
    return a


def get_Y_per_X_all_algos(results_df, scene, X, Y):
    return reduce(lambda df1, df2: pd.merge(df1, df2, left_index=True ,right_index=True, how="outer"),
                  [get_Y_per_X(results_df, scene, solver_class.__name__, X, Y)
                   for solver_class in ALGOS])


def lengths_per_budget(results_df, scene):
    return get_Y_per_X_all_algos(results_df, scene, X="budget_avg", Y="total_path_length_avg")


def lengths_per_calc_time(results_df, scene):
    return get_Y_per_X_all_algos(results_df, scene, X="calc_time_avg", Y="total_path_length_avg")


# create_table_func = lengths_per_budget
create_table_func = lengths_per_calc_time

results_df = pd.read_csv(results_file_path)
summary_file_path = f"{os.path.dirname(results_file_path)}/summary_{create_table_func.__name__}.xlsx"
assert not os.path.exists(summary_file_path)
with pd.ExcelWriter(summary_file_path, engine="openpyxl") as writer:
    for scene in scenes:
        create_table_func(results_df, scene).to_excel(writer, sheet_name=get_filename(scene))
        remove_style_from_worksheet(writer.sheets[get_filename(scene)])

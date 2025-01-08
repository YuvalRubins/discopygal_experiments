import os
import sys
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib
from scipy.stats import pearsonr

fig_num = 0

def plot(X, Y, x_name, y_name, labels=None):
    global fig_num
    plt.figure(fig_num)
    fig_num += 1

    if labels:
        label_names = sorted(list(set(labels)))
        if len(label_names) <= 10:
            cmap = matplotlib.colormaps.get_cmap("tab10")
        elif len(label_names) <= 20:
            cmap = matplotlib.colormaps.get_cmap("tab20")
        else:
            raise IndexError("Too many labels!")

        colors = [cmap(label_names.index(label)) for label in labels]
        legend_handles = [
                plt.Line2D([0], [0], marker='o', color='w', markerfacecolor=cmap(idx), markersize=8, label=name)
                for idx, name in enumerate(label_names)
            ]
        plt.legend(handles=legend_handles, title="Labels", loc="upper left", bbox_to_anchor=(1,1), fontsize=5)
    else:
        colors = None

    plt.scatter(X, Y, color=colors, alpha=0.25)
    plt.xlabel(x_name)
    plt.ylabel(y_name)


def create_df_from_dict_column(scenarios_results: pd.DataFrame, dict_column_name: str):
    records = []
    for i in range(len(scenarios_results)):
        # operations_count.loc[i] = add_missing_operations(eval(all_scenarios['operations_count'][i]), operations)
        records.append(eval(scenarios_results[dict_column_name][i]))
    df = pd.DataFrame.from_records(records)
    df = df.fillna(0)
    return df

def plot_drrt_star(all_scenarios, results):
    group_per_scenario = [os.path.basename(results.loc[all_scenarios.loc[i, 'scenario_index'], 'scene_path']) for i in range(len(all_scenarios))]
    operations_count = create_df_from_dict_column(all_scenarios, "operations_count")
    mean_time_to_inc_operation_ratio = create_df_from_dict_column(all_scenarios, "mean_time_to_inc_operation_ratio")
    std_time_to_inc_operation_ratio = create_df_from_dict_column(all_scenarios, "std_time_to_inc_operation_ratio")

    weights = {operation: 1 for operation in operations_count.columns}
    # weights['set_intersection'] = 0
    # weights['TensorRoadmap.cost'] = 0
    # print(weights)
    print("operation counts STDs: " + str({name: np.round(operations_count[name].std()) for name in operations_count.columns}))
    operations_count['budget'] = sum([weights[operation] * operations_count[operation] for operation in operations_count.columns])

    print(f"Pearson correlation coefficient: {pearsonr(all_scenarios['calc_time'], operations_count['budget'])[0]}")
    plot(all_scenarios['calc_time'], operations_count['budget'], 'calc_time', 'budget', group_per_scenario)

    plot(range(len(all_scenarios['calc_time'])), all_scenarios['calc_time'], 'scenario_index', 'calc_time', group_per_scenario)
    plot(range(len(operations_count['budget'])), operations_count['budget'], 'scenario_index', 'budget', group_per_scenario)
    plot(range(len(operations_count['budget'])), operations_count['budget'] / all_scenarios['calc_time'], 'scenario_index', 'budget_to_calc_time_ratio', group_per_scenario)
    for operation in mean_time_to_inc_operation_ratio.columns:
        plot(range(len(mean_time_to_inc_operation_ratio[operation])), mean_time_to_inc_operation_ratio[operation], 'scenario_index', operation, scene_per_scenario)
        # plot(operations_count[operation], mean_time_to_inc_operation_ratio[operation], f'{operation} count', 'mean_time_to_inc_operation_ratio', scene_per_scenario)
        # plot(range(len(std_time_to_inc_operation_ratio[operation])), std_time_to_inc_operation_ratio[operation], 'scenario_index', operation, scene_per_scenario)
        # plot(all_scenarios['calc_time'], operations_count[operation], 'calc_time', operation)
    # plot(all_scenarios['calc_time'], operations_count['shortest_path_length'], 'calc_time', 'path_length')

def plot_multi_algs(all_scenarios, results):
    group_per_scenario = [results.loc[all_scenarios.loc[i, 'scenario_index'], 'solver_class'] for i in range(len(all_scenarios))]
    plot(all_scenarios['calc_time'], all_scenarios['budget'], 'calc_time', 'budget', group_per_scenario)
    plot(range(len(all_scenarios['budget'])), all_scenarios['budget'] / all_scenarios['calc_time'], 'scenario_index', 'budget_to_calc_time_ratio', group_per_scenario)
    plt.show()


def main():
    results_dir_path = sys.argv[1]
    all_scenarios = pd.read_csv(f"{results_dir_path}/all_scenarios.csv")
    results = pd.read_csv(f"{results_dir_path}/results.csv")

    plot_multi_algs(all_scenarios, results)
    # plot_drrt_star(all_scenarios, results)

    plt.show()


if __name__ == "__main__":
    main()

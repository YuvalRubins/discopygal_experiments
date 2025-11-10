import os
import sys
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib
from scipy.stats import pearsonr

fig_num = 0

def plot(X, Y, x_name, y_name, labels=None, title=None, labels_filter: callable = None):
    global fig_num
    plt.figure(fig_num)
    fig_num += 1

    if labels and labels_filter:
        label_names = sorted(list(set(labels)))
        filtered_X = []
        filtered_Y = []
        filtered_labels = []
        for i, label in enumerate(labels):
            if labels_filter(label):
                filtered_X.append(X[i])
                filtered_Y.append(Y[i])
                filtered_labels.append(label)

        X = filtered_X
        Y = filtered_Y
        labels = filtered_labels

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

    if len(X) > 10_000:
        size = 0.5
        alpha = 1
    else:
        size = None
        alpha = 0.25

    plt.scatter(X, Y, s=size, color=colors, alpha=alpha)
    plt.xlabel(x_name)
    plt.ylabel(y_name)
    if title:
        plt.title(title)


def create_df_from_dict_column(scenarios_results: pd.DataFrame, dict_column_name: str):
    records = []
    for i in range(len(scenarios_results)):
        # operations_count.loc[i] = add_missing_operations(eval(all_scenarios['operations_count'][i]), operations)
        try:
            records.append(eval(scenarios_results[dict_column_name][i]))
        except TypeError:
            records.append({})
    df = pd.DataFrame.from_records(records)
    df = df.fillna(0)
    return df


def get_expected_budget(row):
    algorithm, parameters = row
    parameters = eval(parameters)
    return {
        "PRM": lambda params: params["num_landmarks"],
        "RRT": lambda params: params["num_landmarks"],
        "RRT_star": lambda params: params["num_landmarks"],
        "dRRT": lambda params: 10 * params["num_landmarks"],
        "dRRT_star": lambda params: 100 * params["num_landmarks"],
        "LBT_RRT": lambda params: params["num_landmarks"],
        "BiRRT": lambda params: params["num_landmarks"],
        "StaggeredGrid": lambda params: 0
    }[algorithm](parameters)


def plot_drrt_star(all_scenarios):
    group_per_scenario = [os.path.basename(all_scenarios.loc[i, 'scene_path']) for i in range(len(all_scenarios))]
    operations_count = create_df_from_dict_column(all_scenarios, "operations_count")
    mean_time_to_inc_operation_ratio = create_df_from_dict_column(all_scenarios, "mean_time_to_inc_operation_ratio")
    std_time_to_inc_operation_ratio = create_df_from_dict_column(all_scenarios, "std_time_to_inc_operation_ratio")

    weights = {operation: 1 for operation in operations_count.columns}
    print(weights)
    print("operation counts STDs: " + str({name: np.round(operations_count[name].std()) for name in operations_count.columns}))
    operations_count['budget'] = sum([weights[operation] * operations_count[operation] for operation in operations_count.columns])

    print(f"Pearson correlation coefficient: {pearsonr(all_scenarios['calc_time'], operations_count['budget'])[0]}")
    plot(all_scenarios['calc_time'], operations_count['budget'], 'calc_time', 'budget', group_per_scenario)

    # plot(range(len(all_scenarios['calc_time'])), all_scenarios['calc_time'], 'scenario_index', 'calc_time', group_per_scenario)
    # plot(range(len(operations_count['budget'])), operations_count['budget'], 'scenario_index', 'budget', group_per_scenario)
    # plot(range(len(operations_count['budget'])), operations_count['budget'] / all_scenarios['calc_time'], 'scenario_index', 'budget_to_calc_time_ratio', group_per_scenario)
    # for operation in mean_time_to_inc_operation_ratio.columns:
        # plot(range(len(operations_count[operation])), operations_count[operation], 'scenario_index', f'{operation} count', group_per_scenario)
        # plot(range(len(mean_time_to_inc_operation_ratio[operation])), mean_time_to_inc_operation_ratio[operation], 'scenario_index', operation, group_per_scenario)
        # plot(operations_count[operation], mean_time_to_inc_operation_ratio[operation], f'{operation} count', 'mean_time_to_inc_operation_ratio', group_per_scenario)
        # plot(range(len(std_time_to_inc_operation_ratio[operation])), std_time_to_inc_operation_ratio[operation], 'scenario_index', operation, group_per_scenario)
        # plot(all_scenarios['calc_time'], operations_count[operation], 'calc_time', operation)
    plot(all_scenarios['calc_time'], all_scenarios['total_path_length'], 'calc_time', 'path_length', group_per_scenario)
    plot(operations_count['budget'], all_scenarios['total_path_length'], 'budget', 'path_length', group_per_scenario)


def plot_multi_algs(all_scenarios):
    alg_per_scenario = [all_scenarios.loc[i, 'solver_class'] for i in range(len(all_scenarios))]
    scene_per_scenario = [all_scenarios.loc[i, 'scene_path'] for i in range(len(all_scenarios))]
    scenes = set(scene_per_scenario)
    algs = set(alg_per_scenario)
    scenarios_per_scene = {scene: [scenario for scenario in range(len(all_scenarios)) if scene_per_scenario[scenario] == scene]
                           for scene in scenes}
    scenarios_per_alg = {alg: [scenario for scenario in range(len(all_scenarios)) if alg_per_scenario[scenario] == alg]
                           for alg in algs}

    operations_count = create_df_from_dict_column(all_scenarios, "operations_count")
    mean_time_to_inc_operation_ratio = create_df_from_dict_column(all_scenarios, "mean_time_to_inc_operation_ratio")
    std_time_to_inc_operation_ratio = create_df_from_dict_column(all_scenarios, "std_time_to_inc_operation_ratio")
    weights = {operation: 1 for operation in operations_count.columns}
    all_scenarios['budget'] = sum([weights[operation] * operations_count[operation] for operation in operations_count.columns])
    all_scenarios['expected_budget'] = all_scenarios[["solver_class", "parameters"]].apply(get_expected_budget, axis=1)

    staggered_grid_lengths = all_scenarios[all_scenarios["solver_class"] == "StaggeredGrid"][["scene_path", "total_path_length"]]
    staggered_grid_lengths = staggered_grid_lengths.rename(columns={"total_path_length": "staggered_grid_path_length"})
    all_scenarios = all_scenarios.merge(staggered_grid_lengths, on="scene_path", how="left")
    all_scenarios["total_path_length_ratio_to_staggered_grid"] = all_scenarios["total_path_length"] / all_scenarios["staggered_grid_path_length"]

    def plot_per_key(x: str, y: str, scenarios_per_key: dict):
        for key in scenarios_per_key:
            plot(all_scenarios[x][scenarios_per_key[key]],
                 all_scenarios[y][scenarios_per_key[key]], x, y,
                 [alg_per_scenario[i] for i in scenarios_per_key[key]],
                 key)

    # plot_per_key("calc_time", "total_path_length", scenarios_per_scene)
    # plot_per_key("budget", "total_path_length", scenarios_per_scene)
    # plot_per_key("calc_time", "total_path_length", scenarios_per_alg)
    # plot_per_key("budget", "total_path_length", scenarios_per_alg)

    # plot(all_scenarios['calc_time'], all_scenarios['budget'], 'calc_time', 'budget', alg_per_scenario, title="Budget by Calculation time", labels_filter=lambda s: s != "StaggeredGrid")
    plot(all_scenarios['budget'], all_scenarios['calc_time'], 'budget', 'calc_time', alg_per_scenario, title="Calculation time by Budget", labels_filter=lambda s: s != "StaggeredGrid")
    # plot(all_scenarios['calc_time'], all_scenarios['budget'], 'calc_time', 'budget', alg_per_scenario, labels_filter=lambda s: s not in ["LBT_RRT", "dRRT_star"])

    # plot(range(len(all_scenarios['budget'])), all_scenarios['budget'] / all_scenarios['calc_time'], 'scenario_index', 'budget_to_calc_time_ratio', alg_per_scenario)
    # plot(all_scenarios['calc_time'], all_scenarios['total_path_length'], 'calc_time', 'path_length', alg_per_scenario)
    # plot(all_scenarios['budget'], all_scenarios['total_path_length'], 'budget', 'path_length', alg_per_scenario)
    plot(all_scenarios['budget'], all_scenarios['total_path_length_ratio_to_staggered_grid'], 'budget', 'path_length_ratio', alg_per_scenario, labels_filter=lambda s: s != "StaggeredGrid")
    plot(all_scenarios['calc_time'], all_scenarios['total_path_length_ratio_to_staggered_grid'], 'calc_time', 'path_length_ratio', alg_per_scenario, labels_filter=lambda s: s != "StaggeredGrid")
    # plot(all_scenarios['calc_time'], all_scenarios['total_path_length'], 'calc_time', 'path_length', alg_per_scenario, labels_filter=lambda s: s == "StaggeredGrid")

    # for operation in mean_time_to_inc_operation_ratio.columns:
        # plot(all_scenarios['scenario_index'], operations_count[operation], 'scenario_index', 'operation count', alg_per_scenario, operation)
        # plot(all_scenarios['scenario_index'], mean_time_to_inc_operation_ratio[operation], 'scenario_index', 'mean time to inc operation ratio', alg_per_scenario, operation)
    # plot(all_scenarios['expected_budget'], all_scenarios['budget'], 'Expected budget', 'Actual budget', alg_per_scenario, labels_filter=lambda s: s != "StaggeredGrid")

    for scene in scenes:
        scenarios = all_scenarios[all_scenarios["scene_path"] == scene]
        alg_per_scenario_for_scene = [scenarios.loc[i, 'solver_class'] for i in scenarios.index]
        # plot(range(len(scenarios['scenario_index'])), scenarios['total_path_length'], 'index', 'total_path_length', alg_per_scenario_for_scene, title=scene)
        # plot(scenarios['calc_time'], scenarios['total_path_length'], 'calc_time', 'total_path_length', alg_per_scenario_for_scene, title=scene)
        plot(scenarios['calc_time'], scenarios['total_path_length_ratio_to_staggered_grid'], 'calc_time', 'path_length_ratio', alg_per_scenario_for_scene, title=scene)


def main():
    all_scenarios_file = sys.argv[1]
    all_scenarios = pd.read_csv(all_scenarios_file)

    plot_multi_algs(all_scenarios)
    # plot_drrt_star(all_scenarios)

    plt.show()


if __name__ == "__main__":
    main()

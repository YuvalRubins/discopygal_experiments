import sys
import pandas as pd
import matplotlib.pyplot as plt
from scipy.stats import pearsonr



def plot_budget_by_time(time, budget):
    plt.scatter(time, budget)
    plt.xlabel('Time')
    plt.ylabel('Budget')
    plt.show()


def add_missing_operations(scenario_count: dict, all_operations: list):
    for operation in all_operations:
        if operation not in scenario_count:
            scenario_count[operation] = 0

    return pd.Series(scenario_count)


def main():
    all_scenarios_dir_path = sys.argv[1]
    all_scenarios = pd.read_csv(all_scenarios_dir_path)

    operations = eval(all_scenarios['operations_count'][0]).keys()

    operations_count = pd.DataFrame(columns=operations)
    for i in range(len(all_scenarios)):
        operations_count.loc[i] = add_missing_operations(eval(all_scenarios['operations_count'][i]), operations)

    weights = {operation: 1 for operation in operations}
    weights["ObjectCollisionDetection.is_point_valid"] = 1
    # print(weights)

    operations_count['budget'] = sum([weights[operation] * operations_count[operation] for operation in operations])

    print(f"Pearson correlation coefficient: {pearsonr(all_scenarios['calc_time'], operations_count['budget'])[0]}")
    # plot_budget_by_time(all_scenarios['calc_time'], operations_count['budget'])


if __name__ == "__main__":
    main()

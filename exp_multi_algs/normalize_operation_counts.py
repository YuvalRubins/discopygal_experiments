import sys
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy.stats import pearsonr


def plot(X, Y, x_name, y_name):
    plt.scatter(X, Y)
    plt.xlabel(x_name)
    plt.ylabel(y_name)
    plt.show()


def main():
    all_scenarios_dir_path = sys.argv[1]
    all_scenarios = pd.read_csv(all_scenarios_dir_path)

    # operations = eval(all_scenarios['operations_count'][0]).keys()

    operations_count_dict = []
    for i in range(len(all_scenarios)):
        # operations_count.loc[i] = add_missing_operations(eval(all_scenarios['operations_count'][i]), operations)
        operations_count_dict.append(eval(all_scenarios['operations_count'][i]))
    operations_count = pd.DataFrame.from_records(operations_count_dict)
    operations_count = operations_count.fillna(0)

    weights = {operation: 1 for operation in operations_count.columns}
    # weights["NearestNeighborsCached.k_nearest"] = 0
    weights["NearestNeighbors_sklearn.k_nearest"] = 0
    # print(weights)
    print("operation counts STDs: " + str({name: np.round(operations_count[name].std()) for name in operations_count.columns}))

    operations_count['budget'] = sum([weights[operation] * operations_count[operation] for operation in operations_count.columns])

    print(f"Pearson correlation coefficient: {pearsonr(all_scenarios['calc_time'], operations_count['budget'])[0]}")
    plot(all_scenarios['calc_time'], operations_count['budget'], 'calc_time', 'budget')
    # plot(all_scenarios['calc_time'], operations_count['shortest_path_length'], 'calc_time', 'path_length')


if __name__ == "__main__":
    main()

from pht_federated.aggregator.schemas.dataset_statistics import *
from pht_federated.aggregator.services.discovery import statistics

from pht_federated.aggregator.schemas.dataset_statistics import *
from pht_federated.aggregator.services.discovery import statistics
import numpy as np
import pandas as pd
from fastapi.encoders import jsonable_encoder


def get_example_objects():
    #data_path = "data/train_data_titanic.csv"
    data_path = "C:/Users/felix/PycharmProjects/federated/pht_federated/tests/aggregator/data/train_data_titanic.csv"
    df = pd.read_csv(data_path)
    df_split = np.array_split(df, 3)

    stats1_json = jsonable_encoder(statistics.get_discovery_statistics(df_split[0]))
    stats2_json = jsonable_encoder(statistics.get_discovery_statistics(df_split[1]))
    # stats3_json = jsonable_encoder(statistics.get_discovery_statistics(df_split[2]))
    # print("Resulting DataSetStatistics from diabetes_dataset : {} + type {}".format(stats_df, type(stats_df)))

    stats_1 = {
        "item_count": stats1_json["item_count"],
        "feature_count": stats1_json["feature_count"],
        "column_information": stats1_json["column_information"],
    }

    stats_2 = {
        "item_count": stats2_json["item_count"],
        "feature_count": stats2_json["feature_count"],
        "column_information": stats2_json["column_information"],
    }

    unstructured_col = {'type': 'unstructured',
                        'title': 'image_data',
                        'not_na_elements': 145,
                        'number_targets': 8,
                        'target_counts': {'Target1': 5,
                                          'Target2': 140},
                        'most_frequent_target': 'Target2',
                        'frequency': 140}

    equal_col = {'type': 'equal',
                 'title': 'race',
                 'value': 'human'}

    stats_1["column_information"].append(unstructured_col)
    stats_1["column_information"].append(equal_col)

    dataset_statistics1 = DatasetStatistics(**stats_1)
    dataset_statistics2 = DatasetStatistics(**stats_2)

    return dataset_statistics1, dataset_statistics2



def compare_objects(dataset_statistics: DatasetStatistics, dataset_statistics_2: DatasetStatistics):

    stats_dict = dataset_statistics.dict()
    stats_dict2 = dataset_statistics_2.dict()

    stats_dict = stats_dict["column_information"]
    stats_dict2 = stats_dict2["column_information"]

    stats_dict_keys = [list(x.keys()) for x in stats_dict]
    stats_dict_keys = set([x for l in stats_dict_keys for x in l])

    stats_dict2_keys = [list(x.keys()) for x in stats_dict2]
    stats_dict2_keys = set([x for l in stats_dict2_keys for x in l])

    print("Stats_Dict_Keys: ".format(stats_dict_keys))

    # find intersection
    intersection = [x for x in stats_dict_keys if x in stats_dict2_keys]
    print("Intersection between object 1 and 2: ".format(intersection))

    # find difference (a - b)
    diff1 = list(set(stats_dict_keys).difference(set(stats_dict2_keys)))
    print("Difference between object1 - object2".format(diff1))

    # find difference (b - a)
    diff2 = list(set(stats_dict2_keys).difference(set(stats_dict_keys)))
    print("Difference between object2 - object1".format(diff2))

#test whether if one column key not exists if the column name is still in the object or not

test1, test2 = get_example_objects()
compare_objects(test1, test2)

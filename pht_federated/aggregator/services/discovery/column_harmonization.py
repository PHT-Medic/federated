from pht_federated.aggregator.schemas.dataset_statistics import *
from pht_federated.aggregator.services.discovery import statistics
from typing import List
from pht_federated.aggregator.schemas.dataset_statistics import *
from pht_federated.aggregator.services.discovery import statistics
import numpy as np
import pandas as pd
from fastapi.encoders import jsonable_encoder
import logging


def get_example_objects():
    #data_path = "data/train_data_titanic.csv"
    data_path = "C:/Users/felix/PycharmProjects/federated/pht_federated/tests/aggregator/data/train_data_titanic.csv"
    df = pd.read_csv(data_path)
    df_split = np.array_split(df, 4)

    stats1_json = jsonable_encoder(statistics.get_discovery_statistics(df_split[0]))
    stats2_json = jsonable_encoder(statistics.get_discovery_statistics(df_split[1]))
    stats3_json = jsonable_encoder(statistics.get_discovery_statistics(df_split[2]))
    stats4_json = jsonable_encoder(statistics.get_discovery_statistics(df_split[3]))
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

    stats_3 = {
        "item_count": stats3_json["item_count"],
        "feature_count": stats3_json["feature_count"],
        "column_information": stats3_json["column_information"],
    }

    stats_4 = {
        "item_count": stats4_json["item_count"],
        "feature_count": stats4_json["feature_count"],
        "column_information": stats4_json["column_information"],
    }

    unstructured_col = {'type': 'unstructured',
                        'title': 'image_data',
                        'not_na_elements': 145,
                        'number_targets': 8,
#                        'target_counts': {'Target1': 5,
#                                          'Target2': 140},
#                        'most_frequent_target': 'Target2',
                        'frequency': 140}

    unstructured_col2 = {'type': 'unstructured',
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
    stats_3["column_information"].append(unstructured_col2)

    dataset_statistics1 = DatasetStatistics(**stats_1)
    dataset_statistics2 = DatasetStatistics(**stats_2)
    dataset_statistics3 = DatasetStatistics(**stats_3)
    dataset_statistics4 = DatasetStatistics(**stats_4)

    return dataset_statistics1, dataset_statistics2, dataset_statistics3, dataset_statistics4



def compare_objects(object_list: List[DatasetStatistics]):
    """
    :type listOfObjects: list<Object>
    """
    logging.getLogger().setLevel(logging.INFO)

    intersection_keys = []
    difference_keys = []

    for x in range(len(object_list[:-1])):
        stats_dict = object_list[x].dict()
        stats_dict2 = object_list[x+1].dict()

        stats_dict = stats_dict["column_information"]
        stats_dict2 = stats_dict2["column_information"]

        stats_dict_filtered = filter_none_values(stats_dict)
        stats_dict2_filtered = filter_none_values(stats_dict2)

        stats_dict_keys = [list(x.keys()) for x in stats_dict_filtered]
        stats_dict_keys = set([x for l in stats_dict_keys for x in l])

        stats_dict2_keys = [list(x.keys()) for x in stats_dict2_filtered]
        stats_dict2_keys = set([x for l in stats_dict2_keys for x in l])

        # find intersection
        intersection = [x for x in stats_dict_keys if x in stats_dict2_keys]
        logging.info("Intersection between object {} and {} of list: {} ".format(x, x+1, intersection))

        # find difference (a - b)
        diff1 = list(set(stats_dict_keys).difference(set(stats_dict2_keys)))
        #logging.info("Difference between object {} - object {} of list: {}".format(x, x+1, diff1))

        # find difference (b - a)
        diff2 = list(set(stats_dict2_keys).difference(set(stats_dict_keys)))
        #logging.info("Difference between object {} - object {} of list: {}".format(x+1, x, diff2))

        logging.info("Difference between object {} - object {} of list: {}".format(x+1, x, diff1 + diff2))

        intersection_keys.append(intersection)
        difference_keys.append(diff1 + diff2)


    intersection_keys = list(set(intersection_keys[0]).intersection(*intersection_keys[1:]))
    logging.info("Intersection Keys : {}".format(intersection_keys))

    difference_keys = list(set([x for l in difference_keys for x in l]))
    logging.info("Difference Keys : {}".format(difference_keys))



def compare_two_objects(dataset_statistics: DatasetStatistics, dataset_statistics_2: DatasetStatistics):
    """
    :type listOfObjects: list<Object>
    """
    logging.getLogger().setLevel(logging.INFO)

    stats_dict = dataset_statistics.dict()
    stats_dict2 = dataset_statistics_2.dict()

    stats_dict = stats_dict["column_information"]
    stats_dict2 = stats_dict2["column_information"]

    stats_dict_keys = [list(x.keys()) for x in stats_dict]
    stats_dict_keys = set([x for l in stats_dict_keys for x in l])

    stats_dict2_keys = [list(x.keys()) for x in stats_dict2]
    stats_dict2_keys = set([x for l in stats_dict2_keys for x in l])

    print("Stats_Dict_Keys: {} ".format(stats_dict_keys))

    # find intersection
    intersection = [x for x in stats_dict_keys if x in stats_dict2_keys]
    logging.info("Intersection between object 1 and 2: {} ".format(intersection))

    # find difference (a - b)
    diff1 = list(set(stats_dict_keys).difference(set(stats_dict2_keys)))
    logging.info("Difference between object1 - object2: {}".format(diff1))

    # find difference (b - a)
    diff2 = list(set(stats_dict2_keys).difference(set(stats_dict_keys)))
    logging.info("Difference between object2 - object1: {}".format(diff2))

def filter_none_values(column_list: list):

    filtered_list = []

    for stats_dict in column_list:
        filtered_object = {k: v for k, v in stats_dict.items() if v is not None}
        filtered_list.append(filtered_object)

    return filtered_list


test1, test2, test3, test4 = get_example_objects()
compare_objects([test1, test2, test3, test4])

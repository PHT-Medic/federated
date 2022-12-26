from pht_federated.aggregator.schemas.dataset_statistics import *

import numpy as np
import pandas as pd
import sklearn
from fastapi.encoders import jsonable_encoder
from sklearn.datasets import load_breast_cancer

from pht_federated.aggregator.services.discovery import statistics


def get_example_object():
    #diabetes_dataset = sklearn.datasets.load_diabetes(return_X_y=False, as_frame=False)

    #df = pd.DataFrame(
    #    diabetes_dataset["data"], columns=diabetes_dataset["feature_names"]
    #)
    #df["target"] = diabetes_dataset["target"]
    data_path = "C:/Users/felix\PycharmProjects/federated/pht_federated/tests/aggregator/data/train_data_titanic.csv"
    df = pd.read_csv(data_path)
    df_split = np.array_split(df, 3)

    stats1_json = jsonable_encoder(statistics.get_discovery_statistics(df_split[0]))
    #stats2_json = jsonable_encoder(statistics.get_discovery_statistics(df_split[1]))
    #stats3_json = jsonable_encoder(statistics.get_discovery_statistics(df_split[2]))
    # print("Resulting DataSetStatistics from diabetes_dataset : {} + type {}".format(stats_df, type(stats_df)))

    stats_1 = {
            "item_count": stats1_json["item_count"],
            "feature_count": stats1_json["feature_count"],
            "column_information": stats1_json["column_information"],
        }

    dataset_statistics1 = DatasetStatistics(**stats_1)

    #print(dataset_statistics1)

    return dataset_statistics1

def object_to_list(dataset_statistics_object: DatasetStatistics) -> list:

    object_list_int = []
    object_list_tuple = []

    print("Dataset Statistics Object : {}".format(dataset_statistics_object.json()))
    stats_dict = dataset_statistics_object.dict()

    object_list_int.append(stats_dict["item_count"])
    object_list_int.append(stats_dict["feature_count"])

    object_list_tuple.append(stats_dict["item_count"])
    object_list_tuple.append(stats_dict["feature_count"])

    for column in stats_dict["column_information"]:
        if column["type"] == "numeric":
            #print("Column : {}".format(column))
            column_list = [
            column["not_na_elements"],
            column["mean"],
            column["std"],
            column["min"],
            column["max"]
            ]
            column_list_new = [round(i * 10000) for i in column_list]
            object_list_tuple.append((column["title"], column_list_new))
            object_list_int.append(column_list_new)
        elif column["type"] == "categorical":
            column_list = [
            column["not_na_elements"],
            column["number_categories"]
            ]
            column_list_new = [round(i * 1000) for i in column_list]
            object_list_tuple.append((column["title"], column_list_new))
            object_list_int.append(column_list_new)

    print("Object List Integer : {}".format(object_list_int))
    print("Object List Tuple : {}".format(object_list_tuple))


    return object_list_tuple


def list_to_object(dataset_statistics_list: list) -> DatasetStatistics:

    item_count = dataset_statistics_list[0]
    feature_count = dataset_statistics_list[1]

    print(dataset_statistics_list[2:])

    dataset_statistics_json = {
            "item_count": item_count,
            "feature_count": feature_count,
        }

    column_information_lst = []

    for column in dataset_statistics_list[2:]:
        if len(column[1]) == 5:
            title = column[0]
            not_na_elements = column[1][0]
            mean = column[1][1]
            std = column[1][2]
            min = column[1][3]
            max = column[1][4]
            column_information_lst.append({
                "type": "numeric",
                "title": title,
                "not_na_elements": not_na_elements,
                "mean": mean,
                "std": std,
                "min": min,
                "max": max
            })
        else:
            title = column[0]
            not_na_elements = column[1][0]
            number_categories = column[1][1]
            column_information_lst.append({
                "type": "categorical",
                "title": title,
                "not_na_elements": not_na_elements,
                "number_categories": number_categories
            })

    dataset_statistics_json["column_information"] = column_information_lst

    dataset_statistics_object = DatasetStatistics(**dataset_statistics_json)

    print("Dataset Statistics Object : {}".format(dataset_statistics_object))

    return dataset_statistics_object


#object_to_list(get_example_object())
list_to_object(object_to_list(get_example_object()))
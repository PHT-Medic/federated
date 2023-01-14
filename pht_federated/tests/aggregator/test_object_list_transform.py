from pht_federated.aggregator.schemas.dataset_statistics import *
from pht_federated.aggregator.services.discovery import statistics
from pht_federated.aggregator.services.discovery import object_list_transform

import numpy as np
import pandas as pd
import sklearn
from fastapi.encoders import jsonable_encoder
from sklearn.datasets import load_breast_cancer


def get_example_object():
    data_path = "data/train_data_titanic.csv"
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


    return dataset_statistics1


def test_object_to_list():

    example_object = get_example_object()
    example_object_dict = example_object.dict()
    example_object_dict_col = example_object_dict["column_information"]
    example_object_dict_col_sorted = object_list_transform.multikeysort(example_object_dict_col, ["type", "title"])
    example_object_dict["column_information"] = example_object_dict_col_sorted

    #print("Example object dict col : {}".format(example_object_dict["column_information"]))

    object_list_int = object_list_transform.object_to_list(example_object)

    object_list_int_masked = [int(i + 10) for i in object_list_int]

    dataset_statistics_object_masked = object_list_transform.list_to_object(object_list_int_masked, example_object)

    object_dict_masked = dataset_statistics_object_masked.dict()

    masked_example_dict_col = [{k:int(v) if type(v) == np.float64 else v for k,v in d.items()} for d in example_object_dict["column_information"]]
    masked_example_dict_col = [{k:int(v+10) if type(v) == int else v for k,v in d.items()} for d in masked_example_dict_col]
    masked_example_dict_col = [{k:None if k != "type" and k != "title" and type(v) != int else v for k,v in d.items()} for d in masked_example_dict_col]

    #print("Example Object dict : {}".format(masked_example_dict_col))
    #print("Object dict masked : {}".format(object_dict_masked["column_information"]))

    assert example_object_dict["feature_count"] + 10 == object_dict_masked["feature_count"]
    assert example_object_dict["item_count"] + 10 == object_dict_masked["item_count"]

    assert masked_example_dict_col == object_dict_masked["column_information"]
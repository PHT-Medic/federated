import numpy as np
import pandas as pd
from fastapi.encoders import jsonable_encoder

from pht_federated.aggregator.schemas.dataset_statistics import *
from pht_federated.aggregator.services.discovery import object_list_transform, statistics


def get_example_object():
    data_path = "data/train_data_titanic.csv"
    df = pd.read_csv(data_path)
    df_split = np.array_split(df, 3)

    stats1_json = jsonable_encoder(statistics.get_discovery_statistics(df_split[0]))
    # stats2_json = jsonable_encoder(statistics.get_discovery_statistics(df_split[1]))
    # stats3_json = jsonable_encoder(statistics.get_discovery_statistics(df_split[2]))
    # print("Resulting DataSetStatistics from diabetes_dataset : {} + type {}".format(stats_df, type(stats_df)))

    stats_1 = {
        "item_count": stats1_json["item_count"],
        "feature_count": stats1_json["feature_count"],
        "column_information": stats1_json["column_information"],
    }

    unstructured_col = {
        "type": "unstructured",
        "title": "image_data",
        "not_na_elements": 145,
        "number_targets": 8,
        "target_counts": {"Target1": 5, "Target2": 140},
        "most_frequent_target": "Target2",
        "frequency": 140,
    }

    equal_col = {"type": "equal", "title": "race", "value": "human"}

    stats_1["column_information"].append(unstructured_col)
    stats_1["column_information"].append(equal_col)

    dataset_statistics1 = DatasetStatistics(**stats_1)

    return dataset_statistics1


def test_object_to_list():

    example_object = get_example_object()
    example_object_dict = example_object.dict()
    example_object_dict_col_sorted = object_list_transform.multikeysort(
        example_object_dict["column_information"], ["type", "title"]
    )
    example_object_dict["column_information"] = example_object_dict_col_sorted

    # transforms all float64 values of dict to integer
    masked_example_dict_col = [
        {k: int(v) if type(v) == np.float64 else v for k, v in d.items()}
        for d in example_object_dict["column_information"]
    ]

    # masks all integer values of dict by adding a scalar=10
    masked_example_dict_col = [
        {k: int(v + 10) if type(v) == int else v for k, v in d.items()}
        for d in masked_example_dict_col
    ]

    # removes all elements of dict that cannot be masked except for type and title
    masked_example_dict_col = [
        {
            k: None if k != "type" and k != "title" and type(v) != int else v
            for k, v in d.items()
        }
        for d in masked_example_dict_col
    ]

    example_object_dict["feature_count"] += 10
    example_object_dict["item_count"] += 10
    example_object_dict["column_information"] = masked_example_dict_col
    example_object_masked = DatasetStatistics(**example_object_dict)

    # transforms example object via function in object_list_transform.py
    object_list_int = object_list_transform.object_to_list(example_object)

    for element in object_list_int:
        assert type(element) == int

    object_list_int_masked = [i + 10 for i in object_list_int]

    # transforms list of integers back to DatasetStatistics object
    dataset_statistics_object_masked = object_list_transform.list_to_object(
        object_list_int_masked, example_object
    )
    object_dict_masked = dataset_statistics_object_masked.dict()

    assert example_object_dict["feature_count"] == object_dict_masked["feature_count"]
    assert example_object_dict["item_count"] == object_dict_masked["item_count"]

    assert masked_example_dict_col == object_dict_masked["column_information"]
    assert dataset_statistics_object_masked == example_object_masked

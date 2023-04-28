import numpy as np
import pandas as pd
import random
from fastapi.encoders import jsonable_encoder

from pht_federated.aggregator.services.discovery import statistics
from pht_federated.aggregator.services.discovery.column_harmonization import *
from pht_federated.aggregator.services.discovery.adjust_tabular_dataset import *


def get_example_objects():
    data_path = "data/train_data_titanic.csv"
    df = pd.read_csv(data_path)
    df_split = np.array_split(df, 4)

    stats1_json = jsonable_encoder(statistics.get_discovery_statistics(df_split[0]))
    stats2_json = jsonable_encoder(statistics.get_discovery_statistics(df_split[1]))
    stats3_json = jsonable_encoder(statistics.get_discovery_statistics(df_split[2]))
    stats4_json = jsonable_encoder(statistics.get_discovery_statistics(df_split[3]))

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

    unstructured_col = {
        "type": "unstructured",
        "title": "MRI_Img",
        "not_na_elements": 145,
        "number_targets": 8,
        "frequency": 140,
    }

    unstructured_col2 = {
        "type": "unstructured",
        "title": "MRI_images",
        "not_na_elements": 145,
        "number_targets": 8,
        "target_counts": {"Target1": 5, "Target2": 140},
        "most_frequent_target": "Target2",
        "frequency": 140,
    }

    unstructured_col3 = {
        "type": "unstructured",
        "title": "FSMI",
        "not_na_elements": 145,
        "number_targets": 8,
        "target_counts": {"Target1": 5, "Target2": 140},
        "most_frequent_target": "Target2",
        "frequency": 140,
    }

    unstructured_col4 = {
        "type": "unstructured",
        "title": "FSMIs",
        "not_na_elements": 145,
        "number_targets": 8,
        "target_counts": {"Target1": 5, "Target2": 140},
        "most_frequent_target": "Target2",
        "frequency": 140,
    }

    unstructured_col5 = {
        "type": "unstructured",
        "title": "Cancer_Images",
        "not_na_elements": 145,
        "number_targets": 8,
        "target_counts": {"Target1": 5, "Target2": 140},
        "most_frequent_target": "Target2",
        "frequency": 140,
    }

    equal_col = {"type": "equal", "title": "race", "value": "human"}

    equal_col2 = {"type": "categorical", "title": "race", "value": "human"}

    equal_col3 = {"type": "equal", "title": "gender", "value": "male"}

    stats_1["column_information"].append(unstructured_col3)
    stats_1["column_information"].append(unstructured_col5)
    stats_1["column_information"].append(unstructured_col)
    stats_1["column_information"].append(equal_col)
    stats_2["column_information"].append(unstructured_col2)
    stats_2["column_information"].append(equal_col2)
    stats_2["column_information"].append(equal_col3)
    stats_2["column_information"].append(unstructured_col4)

    dataset_statistics1 = DatasetStatistics(**stats_1)
    dataset_statistics2 = DatasetStatistics(**stats_2)
    dataset_statistics3 = DatasetStatistics(**stats_3)
    dataset_statistics4 = DatasetStatistics(**stats_4)

    return (
        dataset_statistics1,
        dataset_statistics2,
        dataset_statistics3,
        dataset_statistics4,
        df
    )


def test_difference_report():
    (
        example_dataset,
        example_aggregation,
        example_dataset2,
        example_aggregation2,
        dataframe
    ) = get_example_objects()

    difference_report = compare_two_datasets(
        example_dataset, example_aggregation, "test"
    )
    difference_report2 = compare_two_datasets(
        example_dataset2, example_aggregation2, "test2"
    )

    assert difference_report["status"] == "failed"
    assert difference_report2["status"] == "passed"

    errors = [column["column_name"] for column in difference_report["errors"]]
    #assert errors == ["race", "Cancer_Images", "gender", "MRI_images", "FSMIs"]

    #Add new column to dataframe for testing -> suggested type: categorical
    race_col_entries = ["human" for x in range(891)]
    race_col_entries[889] = 722
    race_col_entries[890] = 888
    dataframe = dataframe.assign(race=race_col_entries)

    #Add new column to dataframe for testing -> suggested type: numerical
    percentage_col_entries = [random.randint(0,100) for x in range(891)]
    percentage_col_entries[560] = "77"
    percentage_col_entries[561] = "48ix"
    dataframe = dataframe.assign(percentage=percentage_col_entries)

    #Add new column to dataframe for testing -> suggested type: equal
    alive_col_entries = ["yes" for x in range(891)]
    alive_col_entries[320] = "no"
    alive_col_entries[261] = 1
    dataframe = dataframe.assign(alive=alive_col_entries)

    #Add new column to dataframe for testing -> suggested type: unique
    identity_col_entries = [x for x in range(891)]
    identity_col_entries[120] = 220
    identity_col_entries[661] = "554"
    identity_col_entries[662] = "fiftyfive"
    dataframe = dataframe.assign(identity=identity_col_entries)

    #Add new column to dataframe for testing -> suggested type: unstructured
    bytes_col_entries = [b'\x48\x65\x6c\x6c\x6f\x20\x77\x6f\x72\x6c\x64' for x in range(891)]
    bytes_col_entries[120] = b'\x43\x65\x6c\x6c\x6f\x20\x76\x6f\x72\x6c\x64'
    bytes_col_entries[121] = b'\x48\x55\x6c\x6c\x6f\x20\x77\x6f\x71\x6c\x62'
    bytes_col_entries[432] = "fiftyfive"
    bytes_col_entries[783] = 55
    dataframe = dataframe.assign(bytes=bytes_col_entries)

    adjusted_dataset_names = adjust_name_differences(example_dataset, difference_report)

    adjusted_dataset_types = adjust_type_differences(dataframe, example_dataset, difference_report)


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

    local_statistics = {
        "item_count": stats1_json["item_count"],
        "feature_count": stats1_json["feature_count"],
        "column_information": stats1_json["column_information"],
    }

    aggregated_statistics = {
        "item_count": stats2_json["item_count"],
        "feature_count": stats2_json["feature_count"],
        "column_information": stats2_json["column_information"],
    }

    local_statistics2 = {
        "item_count": stats3_json["item_count"],
        "feature_count": stats3_json["feature_count"],
        "column_information": stats3_json["column_information"],
    }

    aggregated_statistics2 = {
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
    categorical_col = {"type": "categorical", "title": "race", "value": "human"}

    categorical_col2 = {"type": "categorical", "title": "percentage", "value": "100"}
    numerical_col2 = {"type": "numeric", "title": "percentage", "mean": "50"}

    categorical_col3 = {"type": "categorical", "title": "alive", "value": "maybe"}
    equal_col3 = {"type": "equal", "title": "alive", "value": "maybe"}

    categorical_col4 = {"type": "categorical", "title": "identity", "value": "identification"}
    unique_col4 = {"type": "unique", "title": "identity", "value": "identification"}

    categorical_col5 = {"type": "categorical", "title": "bytes", "value": "bytes_values"}
    unstruct_col5 = {"type": "unstructured", "title": "bytes", "value": "bytes_values"}

    equal_col4 = {"type": "equal", "title": "gender", "value": "male"}

    local_statistics["column_information"].append(unstructured_col3)
    local_statistics["column_information"].append(unstructured_col5)
    local_statistics["column_information"].append(unstructured_col)
    local_statistics["column_information"].append(equal_col)
    local_statistics["column_information"].append(categorical_col2)
    local_statistics["column_information"].append(categorical_col3)
    local_statistics["column_information"].append(categorical_col4)
    local_statistics["column_information"].append(categorical_col5)

    aggregated_statistics["column_information"].append(unstructured_col2)
    aggregated_statistics["column_information"].append(categorical_col)
    aggregated_statistics["column_information"].append(equal_col4)
    aggregated_statistics["column_information"].append(unstructured_col4)
    aggregated_statistics["column_information"].append(numerical_col2)
    aggregated_statistics["column_information"].append(equal_col3)
    aggregated_statistics["column_information"].append(unique_col4)
    aggregated_statistics["column_information"].append(unstruct_col5)

    dataset_statistics_local = DatasetStatistics(**local_statistics)
    dataset_statistics_aggregated = DatasetStatistics(**aggregated_statistics)

    dataset_statistics_local2 = DatasetStatistics(**local_statistics2)
    dataset_statistics_aggregated2 = DatasetStatistics(**aggregated_statistics2)

    return (
        dataset_statistics_local,
        dataset_statistics_aggregated,
        dataset_statistics_local2,
        dataset_statistics_aggregated2,
        df
    )


def test_difference_report():
    (
        dataset_local,
        dataset_aggregated,
        dataset_local2,
        dataset_aggregated2,
        dataframe
    ) = get_example_objects()

    difference_report = compare_two_datasets(
        dataset_local, dataset_aggregated, "test"
    )
    difference_report2 = compare_two_datasets(
        dataset_local2, dataset_aggregated2, "test2"
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
    percentage_col_entries[761] = "notanumber"
    dataframe = dataframe.assign(percentage=percentage_col_entries)

    #Add new column to dataframe for testing -> suggested type: equal
    alive_col_entries = ["yes" for x in range(891)]
    alive_col_entries[320] = "no"
    alive_col_entries[261] = 1
    dataframe = dataframe.assign(alive=alive_col_entries)

    #Add new column to dataframe for testing -> suggested type: unique
    identity_col_entries = [x for x in range(891)]
    identity_col_entries[120] = 220
    identity_col_entries[421] = 230
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

    #Add new column to dataframe for testing -> suggested type: unstructured
    mri_img_col_entries = [b'\x48\x65\x6c\x6c\x6f\x26\x71\x6f\x72\x6c\x64' for x in range(891)]
    mri_img_col_entries[160] = b'\x43\x65\x6c\x6c\x6f\x20\x76\x6f\x72\x6c\x64'
    mri_img_col_entries[321] = b'\x48\x55\x6c\x6c\x6f\x20\x77\x6f\x71\x6c\x62'
    mri_img_col_entries[512] = "fiftyfive"
    dataframe = dataframe.assign(MRI_Img=mri_img_col_entries)


    #adjusted_dataset_names = adjust_name_differences(dataset_local, difference_report)

    adjusted_dataset_types = adjust_differences(dataframe, dataset_local, difference_report)


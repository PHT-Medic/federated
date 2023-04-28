import re
from typing import List, Tuple
import numpy as np
import pandas as pd
import collections
from pandas.api.types import is_bool_dtype, is_numeric_dtype
from pht_federated.aggregator.schemas.dataset_statistics import DatasetStatistics



def adjust_name_differences(local_dataset_stat: DatasetStatistics, difference_report: dict) -> DatasetStatistics:
    """
    Changes the column names of the local dataset according to the suggested changes provided by the difference report.
    :param local_dataset_stat: summary statistics of the given local dataset
    :param difference_report: Lists differences between local and aggregated datasets and provides hints to resolve them
    :return adjusted_dataset -> Dataset with applied column name changes
    """

    local_dataset_stat = local_dataset_stat.dict()
    #print("Local dataset: {}".format(local_dataset))
    #print("Difference Report: {}".format(difference_report))

    name_errors = [column["hint"] for column in difference_report["errors"] if column["error"]["type"] == "added"]
    #print("Name Errors : {}".format(name_errors))

    name_diffs = [re.findall('"([^"]*)"', errors) for errors in name_errors]
    name_diffs = [error for error in name_diffs if len(error) > 1]
    #print("Name diffs : {}".format(name_diffs))

    for column in local_dataset_stat["column_information"]:
        for diff in name_diffs:
            if column["title"] == diff[0]:
                column["title"] = diff[1]

    #print("Updated local dataset : {}".format(local_dataset))

    return DatasetStatistics(**local_dataset_stat)

def delete_name_differences(local_dataset_stat: DatasetStatistics, difference_report: dict) -> DatasetStatistics:
    """
    Deletes the column names of the local dataset when the respective column is only available locally
    :param local_dataset_stat: summary statistics of the given local dataset
    :param difference_report: Lists differences between local and aggregated datasets and provides hints to resolve them
    :return adjusted_dataset -> Dataset with applied column name changes
    """

    local_dataset_stat = local_dataset_stat.dict()

    name_errors = [column["hint"] for column in difference_report["errors"] if column["error"]["type"] == "added"]
    name_diffs = [re.findall('"([^"]*)"', errors) for errors in name_errors]
    name_diffs = [error for error in name_diffs if len(error) == 1]

    for c in range(len(local_dataset_stat["column_information"])):
        for diff in name_diffs:
            if local_dataset_stat["column_information"][c]["title"] == diff[0]:
                del local_dataset_stat["column_information"][c]

    return DatasetStatistics(**local_dataset_stat)


def adjust_type_differences(local_dataset: pd.DataFrame, local_dataset_stat: DatasetStatistics,
                            difference_report: dict) -> DatasetStatistics:
    """
    Changes the column types of the local dataset according to the suggested changes provided by the difference report
    while taking multiple different mismatching cases into account
    :param local_dataset: Pandas dataframe of the tabular local dataset
    :param local_dataset_stat: summary statistics of the given local dataset
    :param difference_report: Lists differences between local and aggregated datasets and provides hints to resolve them
    :return adjusted_dataset -> Dataset with applied column name changes
    """

    local_dataset_stat = local_dataset_stat.dict()

    #print("Local Dataset : {}".format(local_dataset))
    #print("Local Dataset Statistics : {}".format(local_dataset_stat))
    #print("Difference Report : {}".format(difference_report))

    type_errors = [column["hint"] for column in difference_report["errors"] if column["error"]["type"] == "type"]
    type_diffs = [re.findall('"([^"]*)"', errors) for errors in type_errors]

    row_errors_list = []

    for differences in type_diffs:
        print("Type-Differences : {}".format(differences))
        row_errors_list.append(find_row_errors(local_dataset, differences[0], differences[1]))

    error_report = create_row_error_report(row_errors_list, "test_dataset")

    print("Error Report : {}".format(error_report))




def find_row_errors(local_dataset: pd.DataFrame, column_name: str, column_type: str):
    """
    Checks the column of the local_dataset where the error was found and searches for specific entries that
    violate the desired/likely column type
    :param local_dataset: Local dataset of the user that starts a proposal request over multiple stations
    :param column_name: Name of the column where the type error occured
    :param column_type: Suggested correct column type
    :return: List[Tuple[error_index, error_value, column_name , column_type]]
    """
    row_errors_list = []
    #print("Local Dataset : {} + type {}".format(local_dataset[column_name], type(local_dataset[column_name])))

    if column_type == "categorical":
        row_errors_list = find_categorical_mismatch(local_dataset, column_name, column_type)
    if column_type == "numeric":
        row_errors_list = find_numerical_mismatch(local_dataset, column_name, column_type)
    if column_type == "equal":
        row_errors_list = find_equal_mismatch(local_dataset, column_name, column_type)
    if column_type == "unique":
        row_errors_list = find_unique_mismatch(local_dataset, column_name, column_type)
    if column_type == "unstructured":
        row_errors_list = find_unstructured_mismatch(local_dataset, column_name, column_type)

    return row_errors_list


def create_row_error_report(
    row_errors_list: List[List[Tuple[str, str, str, str]]],
    dataset_name: str,
) -> dict:
    """
    Transforms multiple types of potentially false row-index entries into an error-report that is provided to the
    creator of a proposal
    :param row_errors: Lists errors in specific row indices that do not match the expected data type
    :param dataset_name: String that defines the name of local dataset
    :return: Dictionary which lists type errors in specific rows with hints for correction if possible
    """

    difference_report = {
        "dataset": dataset_name,
        "datatype": "tabular",
        "status": "",
        "errors": [],
    }

    print("Row Errors List : {}".format(row_errors_list))

    # adds errors to difference report where there is a difference in the type of the same column_name
    for row_errors in row_errors_list:
        for error in row_errors:
            print("Error : {}".format(error))
            case = {
                "column_name": error[2],
                "error": {
                    "type": "type",  # missing, type, semantic, extra
                    "suggested_type": error[3],
                    "row_index": error[0][0],
                    "row_value": error[1][0]
                },
                "hint": f"Change type of row entry \"{error[1][0]}\" at index \"{error[0][0]}\" to \"{error[3]}\"",
            }
            difference_report["errors"].append(case)


    return difference_report



def find_categorical_mismatch(local_dataset: pd.DataFrame, column_name: str, column_type: str):

    error_list = []

    for entry in local_dataset[column_name]:
        if not isinstance(entry, str | bool):
            error_index = local_dataset.index[local_dataset[column_name] == entry].tolist()
            error_value = local_dataset[column_name].loc[[error_index[0]]].to_list()
            error_tuple = (error_index, error_value, column_name, column_type)
            error_list.append(error_tuple)

    return error_list


def find_numerical_mismatch(local_dataset: pd.DataFrame, column_name: str, column_type: str):

    error_list = []

    for entry in local_dataset[column_name]:
        if not isinstance(entry, int | float | np.int64 | np.float64):
            error_index = local_dataset.index[local_dataset[column_name] == entry].tolist()
            error_value = local_dataset[column_name].loc[[error_index[0]]].to_list()
            error_tuple = (error_index, error_value, column_name, column_type)
            error_list.append(error_tuple)

    return error_list

def find_equal_mismatch(local_dataset: pd.DataFrame, column_name: str, column_type: str):

    error_list = []

    if not (local_dataset[column_name] == local_dataset[column_name][0]).all():
        unequal_indices = check_same_value(local_dataset[column_name].tolist())

        for index in unequal_indices:
            error_value = local_dataset[column_name].loc[[index]].to_list()
            error_tuple = ([index], error_value, column_name, column_type)
            error_list.append(error_tuple)

    return error_list


def find_unique_mismatch(local_dataset: pd.DataFrame, column_name: str, column_type: str):

    error_list = []

    if len(local_dataset[column_name].tolist()) > len(set(local_dataset[column_name].tolist())):
        dupes = [item for item, count in collections.Counter(local_dataset[column_name].tolist()).items() if count > 1]
        for val in dupes:
            error_index = local_dataset.index[local_dataset[column_name] == val].tolist()
            error_index = [x for x in error_index if x != val]
            error_tuple = (error_index, [val], column_name, column_type)
            error_list.append(error_tuple)

    return error_list


def find_unstructured_mismatch(local_dataset: pd.DataFrame, column_name: str, column_type: str):

    error_list = []

    for entry in local_dataset[column_name]:
        if not type(entry) == bytes:
            error_index = local_dataset.index[local_dataset[column_name] == entry].tolist()
            error_value = local_dataset[column_name].loc[[error_index[0]]].to_list()
            error_tuple = (error_index, error_value, column_name, column_type)
            error_list.append(error_tuple)

    return error_list

def check_same_value(lst):
    unequal_value = next((x for x in lst if x != lst[0]), None)
    if unequal_value is None:
        unequal_indices = []
    else:
        unequal_indices = [i for i in range(len(lst)) if lst[i] != lst[0]]
        #unequal_indices.append(0)
        #TODO - case when first element of list is unqueal to all other elements
    return unequal_indices
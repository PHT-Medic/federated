import collections
import re
from typing import List, Tuple

import numpy as np
import pandas as pd

from pht_federated.aggregator.schemas.dataset_statistics import DatasetStatistics


def adjust_name_differences(
    local_dataset_stat: DatasetStatistics, difference_report: dict
) -> DatasetStatistics:
    """
    Changes the column names of the local dataset according to the suggested changes provided by the difference report.
    :param local_dataset_stat: summary statistics of the given local dataset
    :param difference_report: Lists differences between local and aggregated datasets and provides hints to resolve them
    :return adjusted_dataset -> Dataset with applied column name changes
    """

    local_dataset_stat = local_dataset_stat.dict()
    #print("Difference Report: {}".format(difference_report))

    name_errors = [
        column["hint"]
        for column in difference_report["errors"]
        if column["error"]["type"] == "added"
    ]

    name_diffs = [re.findall('"([^"]*)"', errors) for errors in name_errors]
    name_diffs = [error for error in name_diffs if len(error) > 1]
    print("Name diffs : {}".format(name_diffs))

    for column in local_dataset_stat["column_information"]:
        for diff in name_diffs:
            if column["title"] == diff[0]:
                column["title"] = diff[1]

    return DatasetStatistics(**local_dataset_stat)


def delete_name_differences(
    local_dataset_stat: DatasetStatistics, difference_report: dict
) -> DatasetStatistics:
    """
    Deletes the column names of the local dataset when the respective column is only available locally
    :param local_dataset_stat: summary statistics of the given local dataset
    :param difference_report: Lists differences between local and aggregated datasets and provides hints to resolve them
    :return adjusted_dataset -> Dataset with applied column name changes
    """

    local_dataset_stat = local_dataset_stat.dict()

    name_errors = [
        column["hint"]
        for column in difference_report["errors"]
        if column["error"]["type"] == "added"
    ]
    name_diffs = [re.findall('"([^"]*)"', errors) for errors in name_errors]
    name_diffs = [error for error in name_diffs if len(error) == 1]

    for c in range(len(local_dataset_stat["column_information"])):
        for diff in name_diffs:
            if local_dataset_stat["column_information"][c]["title"] == diff[0]:
                del local_dataset_stat["column_information"][c]

    return DatasetStatistics(**local_dataset_stat)


def adjust_differences(
    local_dataset: pd.DataFrame,
    local_dataset_stat: DatasetStatistics,
    difference_report: dict,
) -> DatasetStatistics:
    """
    Changes the column types and names of the local dataset according to the suggested changes provided by the
    difference report while taking multiple different mismatching cases into account
    :param local_dataset: Pandas dataframe of the tabular local dataset
    :param local_dataset_stat: summary statistics of the given local dataset
    :param difference_report: Lists differences between local and aggregated datasets and provides hints to resolve them
    :return adjusted_dataset -> Dataset with applied column name changes
    """

    local_dataset_stat = local_dataset_stat.dict()

    type_errors = [
        column["hint"]
        for column in difference_report["errors"]
        if column["error"]["type"] == "type"
    ]
    type_diffs = [re.findall('"([^"]*)"', errors) for errors in type_errors]

    name_errors = [
        column["hint"]
        for column in difference_report["errors"]
        if column["error"]["type"] == "added"
    ]
    name_diffs = [re.findall('"([^"]*)"', errors) for errors in name_errors]
    col_error_list = [error for error in name_diffs if len(error) > 1]

    row_errors_list = []

    for differences in type_diffs:
        row_errors_list.append(
            find_row_errors(local_dataset, differences[0], differences[1])
        )

    print("Row Errors List : {}".format(row_errors_list))
    print("Col Errors List : {}".format(col_error_list))

    error_report = create_error_report(row_errors_list, col_error_list, "test_dataset")

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

    if column_type == "categorical":
        row_errors_list = find_categorical_mismatch(
            local_dataset, column_name, column_type
        )
    if column_type == "numeric":
        row_errors_list = find_numerical_mismatch(
            local_dataset, column_name, column_type
        )
    if column_type == "equal":
        row_errors_list = find_equal_mismatch(local_dataset, column_name, column_type)
    if column_type == "unique":
        row_errors_list = find_unique_mismatch(local_dataset, column_name, column_type)
    if column_type == "unstructured":
        row_errors_list = find_unstructured_mismatch(
            local_dataset, column_name, column_type
        )

    return row_errors_list


def create_error_report(
    row_errors_list: List[List[Tuple[str, str, str, str]]],
    col_errors_list: List[List[str]],
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

    for error in col_errors_list:
        case = {
            "column_name": error[0],
            "error": {
                "type": "column_name",  # missing, type, semantic, extra
                "suggested_name": error[1],
            },
            "hint": f'Change name of column: "{error[0]}" to "{error[1]}"',
        }
        difference_report["errors"].append(case)

    # adds errors to difference report where there is a difference in the type of the same column_name
    for row_errors in row_errors_list:
        for error in row_errors:
            case = {
                "column_name": error[2],
                "error": {
                    "type": "type",  # missing, type, semantic, extra
                    "suggested_type": error[3],
                    "row_index": error[0][0],
                    "row_value": error[1][0],
                },
                "hint": f'Change type of row entry: "{error[1][0]}" at index: "{error[0][0]}" to "{error[3]}"',
            }

            if error[3] == "equal":
                case["hint"] = (
                    f'Change type of row entry: "{error[1][0]}" at index: "{error[0][0]}" to'
                    f' the most common element: "{error[4]}"'
                )

            if error[3] == "unique":
                case["hint"] = (
                    f'Change type of row entry: "{error[1][0]}" at index: "{error[0][0]}" to'
                    f" a unique element"
                )

            if error[3] == "unstructured":
                case["hint"] = (
                    f'Change type of row entry: "{error[1][0]}" at index: "{error[0][0]}" to'
                    f' the most common type in this column: "{error[4]}"'
                )

            difference_report["errors"].append(case)

    return difference_report


def find_categorical_mismatch(
    local_dataset: pd.DataFrame, column_name: str, column_type: str
):
    """
    Searches for a column in the local dataset that is supposed to be categorical but contains entries that are not
    :param local_dataset: Local dataset of the user that starts a proposal request over multiple stations
    :param column_name: Name of the column where the type error occured
    :return error_list: List of tuples that contain the index and value of the error, the column name and suggested type
    """

    error_list = []

    for entry in local_dataset[column_name]:
        if not isinstance(entry, str | bool):
            error_index = local_dataset.index[
                local_dataset[column_name] == entry
            ].tolist()
            error_value = local_dataset[column_name].loc[[error_index[0]]].to_list()
            error_tuple = (error_index, error_value, column_name, column_type)
            error_list.append(error_tuple)

    return error_list


def find_numerical_mismatch(
    local_dataset: pd.DataFrame, column_name: str, column_type: str
):
    """
    Searches for a column in the local dataset that is supposed to be numerical but contains entries that are not
    :param local_dataset: Local dataset of the user that starts a proposal request over multiple stations
    :param column_name: Name of the column where the type error occured
    :return error_list: List of tuples that contain the index and value of the error, the column name and suggested type
    """

    error_list = []

    for entry in local_dataset[column_name]:
        if not isinstance(entry, int | float | np.int64 | np.float64):
            error_index = local_dataset.index[
                local_dataset[column_name] == entry
            ].tolist()
            error_value = local_dataset[column_name].loc[[error_index[0]]].to_list()
            error_tuple = (error_index, error_value, column_name, column_type)
            error_list.append(error_tuple)

    return error_list


def find_equal_mismatch(
    local_dataset: pd.DataFrame, column_name: str, column_type: str
):
    """
    Searches for a column in the local dataset that is supposed to be equal value but contains entries that are not
    :param local_dataset: Local dataset of the user that starts a proposal request over multiple stations
    :param column_name: Name of the column where the type error occured
    :return error_list: List of tuples that contain the index and value of the error, the column name, suggested type and
                        most common element in the respective column
    """

    error_list = []

    if not (local_dataset[column_name] == local_dataset[column_name][0]).all():
        unequal_indices = check_same_value(local_dataset[column_name].tolist())

        for index in unequal_indices:
            error_value = local_dataset[column_name].loc[[index]].to_list()
            most_common_element = max(
                set(local_dataset[column_name].tolist()),
                key=local_dataset[column_name].tolist().count,
            )
            error_tuple = (
                [index],
                error_value,
                column_name,
                column_type,
                most_common_element,
            )
            error_list.append(error_tuple)

    return error_list


def find_unique_mismatch(
    local_dataset: pd.DataFrame, column_name: str, column_type: str
):
    """
    Searches for a column in the local dataset that is supposed to be unique value but contains entries that are not
    :param local_dataset: Local dataset of the user that starts a proposal request over multiple stations
    :param column_name: Name of the column where the type error occured
    :return error_list: List of tuples that contain the index and value of the error, the column name and suggested type
    """

    error_list = []

    if len(local_dataset[column_name].tolist()) > len(
        set(local_dataset[column_name].tolist())
    ):
        dupes = [
            item
            for item, count in collections.Counter(
                local_dataset[column_name].tolist()
            ).items()
            if count > 1
        ]
        for val in dupes:
            error_index = local_dataset.index[
                local_dataset[column_name] == val
            ].tolist()
            error_index = [x for x in error_index if x != val]
            error_tuple = (error_index, [val], column_name, column_type)
            error_list.append(error_tuple)

    return error_list


def find_unstructured_mismatch(
    local_dataset: pd.DataFrame, column_name: str, column_type: str
):
    """
    Searches for a column in the local dataset that is supposed to be unstructured data but contains entries that are not
    :param local_dataset: Local dataset of the user that starts a proposal request over multiple stations
    :param column_name: Name of the column where the type error occured
    :return error_list: List of tuples that contain the index and value of the error, the column name, suggested type and
                        most common type in the respective column
    """

    error_list = []

    for entry in local_dataset[column_name]:
        if not type(entry) == bytes:
            most_common_type = type(
                max(
                    set(local_dataset[column_name].tolist()),
                    key=local_dataset[column_name].tolist().count,
                )
            )
            error_index = local_dataset.index[
                local_dataset[column_name] == entry
            ].tolist()
            error_value = local_dataset[column_name].loc[[error_index[0]]].to_list()
            error_tuple = (
                error_index,
                error_value,
                column_name,
                column_type,
                most_common_type,
            )
            error_list.append(error_tuple)

    return error_list


def check_same_value(lst):
    """
    Checks if all elements in a list are the same
     :param lst: List of values
    """
    unequal_value = next((x for x in lst if x != lst[0]), None)
    if unequal_value is None:
        try:
            unequal_value = next((x for x in lst if x != lst[1]), None)
        except:
            unequal_indices = []
    if unequal_value is not None:
        unequal_indices = [i for i in range(len(lst)) if lst[i] != lst[0]]

    return unequal_indices

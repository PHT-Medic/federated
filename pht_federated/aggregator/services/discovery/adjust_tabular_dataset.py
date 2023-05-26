import collections
import re
from typing import List, Tuple

import numpy as np
import pandas as pd

from pht_federated.aggregator.schemas.dataset_statistics import DatasetStatistics
from pht_federated.aggregator.schemas.difference_report import *


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
    # print("Difference Report: {}".format(difference_report))

    name_errors = [
        column["hint"]
        for column in difference_report["errors"]
        if column["error"]["type"] == "added"
    ]

    name_diffs = [re.findall('"([^"]*)"', errors) for errors in name_errors]
    name_diffs = [error for error in name_diffs if len(error) > 1]

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
    difference_report: DifferenceReportBackend,
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

    name_errors = [
        column.hint
        for column in difference_report.errors
        if column.error_type == "added" or column.error_type == "added_name"
    ]
    name_diffs = [re.findall('"([^"]*)"', errors) for errors in name_errors]

    col_error_list = []
    for error in name_diffs:
        if len(error) > 1:
            case = {
                "local_column_name": error[0],
                "aggregator_column_name": error[1],
            }
            col_error_list.append(ColumnHarmonizationError(**case))

    type_errors = [
        column.hint
        for column in difference_report.errors
        if column.error_type == "type"
    ]
    type_diffs = [re.findall('"([^"]*)"', errors) for errors in type_errors]

    row_errors_list = []

    for differences in type_diffs:
        row_errors = find_row_errors(local_dataset, differences[0], differences[1])
        for error in row_errors:
            row_errors_list.append(error)

    row_errors_list = RowHarmonizationResult(**{"row_differences": row_errors_list})
    col_error_list = ColumnHarmonizationResult(**{"column_differences": col_error_list})

    error_report = create_error_report(row_errors_list, col_error_list, "test_dataset")

    return error_report


def find_row_errors(local_dataset: pd.DataFrame, column_name: str, column_type: str):
    """
    Checks the column of the local_dataset where the error was found and searches for specific entries that
    violate the desired/likely column type
    :param local_dataset: Local dataset of the user that starts a proposal request over multiple stations
    :param column_name: Name of the column where the type error occured
    :param column_type: Suggested correct column type
    :return: List[Tuple[error_index, error_value, column_name , column_type]]
    """

    if column_type == "categorical":
        row_errors = find_categorical_mismatch(local_dataset, column_name, column_type)
    if column_type == "numeric":
        row_errors = find_numerical_mismatch(local_dataset, column_name, column_type)
    if column_type == "equal":
        row_errors = find_equal_mismatch(local_dataset, column_name, column_type)
    if column_type == "unique":
        row_errors = find_unique_mismatch(local_dataset, column_name, column_type)
    if column_type == "unstructured":
        row_errors = find_unstructured_mismatch(local_dataset, column_name, column_type)

    return row_errors


def find_categorical_mismatch(
    local_dataset: pd.DataFrame, column_name: str, column_type: str
):
    """
    Searches for a column in the local dataset that is supposed to be categorical but contains entries that are not
    :param local_dataset: Local dataset of the user that starts a proposal request over multiple stations
    :param column_name: Name of the column where the type error occured
    :return error_list: List of dicts that contain the index and value of the error, the column name and suggested type
    """

    row_errors = []

    for entry in local_dataset[column_name]:
        if not isinstance(entry, str | bool):
            error_index = local_dataset.index[
                local_dataset[column_name] == entry
            ].tolist()

            error_value = local_dataset[column_name].loc[[error_index[0]]].to_list()
            error_dict = {
                "index": error_index[0],
                "value": error_value[0],
                "column_name": column_name,
                "aggregator_column_type": column_type,
            }
            row_errors.append(RowHarmonizationError(**error_dict))

    return row_errors


def find_numerical_mismatch(
    local_dataset: pd.DataFrame, column_name: str, column_type: str
) -> List[RowHarmonizationError]:
    """
    Searches for a column in the local dataset that is supposed to be numerical but contains entries that are not
    :param local_dataset: Local dataset of the user that starts a proposal request over multiple stations
    :param column_name: Name of the column where the type error occured
    :param index_list: List of indices that were already checked for errors
    :return error_list: List of RowHarmonizationErrors that contain the index and value of the error, the column name and suggested type
    """

    row_errors = []

    for entry in local_dataset[column_name]:
        if not isinstance(entry, int | float | np.int64 | np.float64):
            error_index = local_dataset.index[
                local_dataset[column_name] == entry
            ].tolist()

            error_value = local_dataset[column_name].loc[[error_index[0]]].to_list()
            error_dict = {
                "index": error_index[0],
                "value": error_value[0],
                "column_name": column_name,
                "aggregator_column_type": column_type,
            }
            row_errors.append(RowHarmonizationError(**error_dict))

    return row_errors


def find_equal_mismatch(
    local_dataset: pd.DataFrame, column_name: str, column_type: str
) -> List[RowHarmonizationError]:
    """
    Searches for a column in the local dataset that is supposed to be equal value but contains entries that are not
    :param local_dataset: Local dataset of the user that starts a proposal request over multiple stations
    :param column_name: Name of the column where the type error occured
    :param index_list: List of indices that were already checked for errors
    :return error_list: List of RowHarmonizationErrors that contain the index and value of the error, the column name, suggested type and
                        most common element in the respective column
    """

    row_errors = []

    if not (local_dataset[column_name] == local_dataset[column_name][0]).all():
        unequal_indices = check_same_value(local_dataset[column_name].tolist())

        for index in unequal_indices:
            error_value = local_dataset[column_name].loc[[index]].to_list()
            most_frequent_element = max(
                set(local_dataset[column_name].tolist()),
                key=local_dataset[column_name].tolist().count,
            )
            error_dict = {
                "index": index,
                "value": error_value[0],
                "column_name": column_name,
                "aggregator_column_type": column_type,
                "most_frequent_element": most_frequent_element,
            }
            row_errors.append(RowHarmonizationError(**error_dict))

    return row_errors


def find_unique_mismatch(
    local_dataset: pd.DataFrame, column_name: str, column_type: str
) -> List[RowHarmonizationError]:
    """
    Searches for a column in the local dataset that is supposed to be unique value but contains entries that are not
    :param local_dataset: Local dataset of the user that starts a proposal request over multiple stations
    :param column_name: Name of the column where the type error occured
    :param index_list: List of indices that were already checked for errors
    :return error_list: List of RowHarmonizationErrors that contain the index and value of the error, the column name and suggested type
    """

    row_errors = []

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
            error_dict = {
                "index": error_index[0],
                "value": val,
                "column_name": column_name,
                "aggregator_column_type": column_type,
            }
            row_errors.append(RowHarmonizationError(**error_dict))

    return row_errors


def find_unstructured_mismatch(
    local_dataset: pd.DataFrame, column_name: str, column_type: str
) -> List[RowHarmonizationError]:
    """
    Searches for a column in the local dataset that is supposed to be unstructured data but contains entries that are not
    :param local_dataset: Local dataset of the user that starts a proposal request over multiple stations
    :param column_name: Name of the column where the type error occured
    :param index_list: List of indices that were already checked for errors
    :return error_list: List of RowHarmonizationErrors that contain the index and value of the error, the column name, suggested type and
                        most common type in the respective column
    """

    row_errors = []

    for entry in local_dataset[column_name]:
        if not type(entry) == bytes:
            type(
                max(
                    set(local_dataset[column_name].tolist()),
                    key=local_dataset[column_name].tolist().count,
                )
            )
            error_index = local_dataset.index[
                local_dataset[column_name] == entry
            ].tolist()
            error_value = local_dataset[column_name].loc[[error_index[0]]].to_list()
            error_dict = {
                "index": error_index[0],
                "value": error_value[0],
                "column_name": column_name,
                "aggregator_column_type": column_type,
                # "most_frequent_type": most_frequent_type
                # TODO: Add most frequent type to error dict
            }
            row_errors.append(RowHarmonizationError(**error_dict))

    return row_errors


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

    for col_error in col_errors_list.column_differences:
        case = {
            "column_name": col_error.local_column_name,
            "error_type": "column_name_error",
            "suggested_name": col_error.aggregator_column_name,
            "hint": f'Change name of column: "{col_error.local_column_name}" to "{col_error.aggregator_column_name}"',
        }
        difference_report["errors"].append(ColumnError(**case))

    # adds errors to difference report where there is a difference in the type of the same column_name
    for row_error in row_errors_list.row_differences:
        case = {
            "column_name": row_error.column_name,
            "error_type": "row_type_error",  # missing, type, semantic, extra
            "suggested_type": row_error.aggregator_column_type,
            "index": row_error.index,
            "value": row_error.value,
            "hint": f'Change type of row entry: "{row_error.value}" at index: "{row_error.index}" to "{row_error.aggregator_column_type}"',
        }

        if row_error.aggregator_column_type == "equal":
            case["hint"] = (
                f'Change type of row entry: "{row_error.value}" at index: "{row_error.index}" to'
                f' the most common element: "{row_error.most_frequent_element}"'
            )

        if row_error.aggregator_column_type == "unique":
            case["hint"] = (
                f'Change type of row entry: "{row_error.value}" at index: "{row_error.index}" to'
                f" a unique element"
            )

        if row_error.aggregator_column_type == "unstructured":
            case["hint"] = (
                f'Change type of row entry: "{row_error.value}" at index: "{row_error.index}" to'
                f' the most common type in this column: "{row_error.most_frequent_type}"'
            )

        difference_report["errors"].append(RowError(**case))

    difference_report = DifferenceReport(**difference_report)

    return difference_report

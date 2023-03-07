from functools import cmp_to_key
from operator import itemgetter as i

from pht_federated.aggregator.schemas.dataset_statistics import *


def object_to_list(dataset_statistics_object: DatasetStatistics) -> list:
    """
    Transforms a DatasetStatistics object to python list of integers that contain all numerical values of the object
    :param dataset_statistics_object: DatasetStatistics
    :return: list of integers
    """

    object_list_int = []

    stats_dict = dataset_statistics_object.dict()

    if "item_count" in stats_dict:
        object_list_int.append(stats_dict["item_count"])

    if "feature_count" in stats_dict:
        object_list_int.append(stats_dict["feature_count"])

    stats_columns = stats_dict["column_information"]
    stats_columns_sorted = multikeysort(stats_columns, ["type", "title"])

    object_list_int = process_column(stats_columns_sorted, object_list_int)

    return object_list_int


def list_to_object(
    dataset_statistics_list: List[DatasetStatistics],
    dataset_statistics_object: DatasetStatistics,
) -> DatasetStatistics:
    """
    Transforms a python list of integers that contain all masked numerical values back to a DatasetStatistics object
    :param dataset_statistics_list: list of DatasetStatistics objects
    :param dataset_statistics_object: dataset summary
    :return: DatasetStatistics
    """
    stats_dict = dataset_statistics_object.dict()

    if "item_count" in stats_dict:
        stats_dict["item_count"] = dataset_statistics_list[0]
    if "feature_count" in stats_dict:
        stats_dict["feature_count"] = dataset_statistics_list[1]

    stats_columns = stats_dict["column_information"]
    stats_columns_sorted = multikeysort(stats_columns, ["type", "title"])

    stats_columns_sorted = retrieve_column(
        stats_columns_sorted, dataset_statistics_list[2:]
    )

    stats_dict["column_information"] = stats_columns_sorted

    dataset_statistics_object = DatasetStatistics(**stats_dict)

    return dataset_statistics_object


def process_column(column_information: list, object_list_int: list) -> list:

    for column in column_information:
        if column["type"] == "categorical":
            object_list_int = process_categorical_column(column, object_list_int)
        elif column["type"] == "numeric":
            object_list_int = process_numerical_column(column, object_list_int)
        elif column["type"] == "unique":
            object_list_int = process_unique_column(column, object_list_int)
        elif column["type"] == "equal":
            pass
        elif column["type"] == "unstructured":
            object_list_int = process_unstructured_column(column, object_list_int)

    return object_list_int


def retrieve_column(column_information: list, dataset_statistics_list: list) -> list:

    for column in column_information:
        if column["type"] == "categorical":
            column, dataset_statistics_list = retrieve_categorical_column(
                column, dataset_statistics_list
            )
        elif column["type"] == "numeric":
            column, dataset_statistics_list = retrieve_numeric_column(
                column, dataset_statistics_list
            )
        elif column["type"] == "unique":
            column, dataset_statistics_list = retrieve_unique_column(
                column, dataset_statistics_list
            )
        elif column["type"] == "equal":
            column, dataset_statistics_list = retrieve_equal_column(
                column, dataset_statistics_list
            )
        elif column["type"] == "unstructured":
            column, dataset_statistics_list = retrieve_unstructured_column(
                column, dataset_statistics_list
            )
    return column_information


def retrieve_categorical_column(
    column: dict, dataset_statistics_list: list
) -> [dict, list]:

    if "not_na_elements" in column:
        column["not_na_elements"] = dataset_statistics_list.pop(0)
    if "number_categories" in column:
        column["number_categories"] = dataset_statistics_list.pop(0)
    if "value_counts" in column:
        del column["value_counts"]
    if "most_frequent_element" in column:
        del column["most_frequent_element"]
    if "frequency" in column:
        column["frequency"] = dataset_statistics_list.pop(0)

    return column, dataset_statistics_list


def retrieve_numeric_column(
    column: dict, dataset_statistics_list: list
) -> [dict, list]:

    if "not_na_elements" in column:
        column["not_na_elements"] = dataset_statistics_list.pop(0)
    if "mean" in column:
        column["mean"] = dataset_statistics_list.pop(0)
    if "std" in column:
        column["std"] = dataset_statistics_list.pop(0)
    if "min" in column:
        column["min"] = dataset_statistics_list.pop(0)
    if "max" in column:
        column["max"] = dataset_statistics_list.pop(0)

    return column, dataset_statistics_list


def retrieve_unique_column(column: dict, dataset_statistics_list: list) -> [dict, list]:
    if "number_of_duplicates":
        column["number_of_duplicates"] = dataset_statistics_list.pop(0)

    return column, dataset_statistics_list


def retrieve_equal_column(column: dict, dataset_statistics_list: list) -> [dict, list]:
    if "title" in column:
        pass
    if "value" in column:
        del column["value"]

    return column, dataset_statistics_list


def retrieve_unstructured_column(
    column: dict, dataset_statistics_list: list
) -> [dict, list]:

    if "not_na_elements" in column:
        column["not_na_elements"] = dataset_statistics_list.pop(0)
    if "number_targets" in column:
        column["number_targets"] = dataset_statistics_list.pop(0)
    if "target_counts" in column:
        del column["target_counts"]
    if "most_frequent_target" in column:
        del column["most_frequent_target"]
    if "frequency" in column:
        column["frequency"] = dataset_statistics_list.pop(0)

    return column, dataset_statistics_list


def process_categorical_column(column: dict, object_list_int: list) -> list:

    if "not_na_elements" in column:
        object_list_int.append(int(column["not_na_elements"]))
    if "number_categories" in column:
        object_list_int.append(int(column["number_categories"]))
    if "frequency" in column:
        object_list_int.append(int(column["frequency"]))

    return object_list_int


def process_numerical_column(column: dict, object_list_int: list) -> list:
    if "not_na_elements" in column:
        object_list_int.append(int(column["not_na_elements"]))
    if "mean" in column:
        object_list_int.append(int(column["mean"]))
    if "std" in column:
        object_list_int.append(int(column["std"]))
    if "min" in column:
        object_list_int.append(int(column["min"]))
    if "max" in column:
        object_list_int.append(int(column["max"]))

    return object_list_int


def process_unique_column(column: dict, object_list_int: list) -> list:
    if "number_of_duplicates" in column:
        object_list_int.append(int(column["number_of_duplicates"]))

    return object_list_int


def process_unstructured_column(column: dict, object_list_int: list) -> list:
    if "not_na_elements" in column:
        object_list_int.append(int(column["not_na_elements"]))
    if "number_targets" in column:
        object_list_int.append(int(column["number_targets"]))
    if "frequency" in column:
        object_list_int.append(int(column["frequency"]))

    return object_list_int


# https://stackoverflow.com/questions/1143671/how-to-sort-objects-by-multiple-keys
def compare(x, y):
    return (x > y) - (x < y)


def multikeysort(items, columns):
    comparers = [
        ((i(col[1:].strip()), -1) if col.startswith("-") else (i(col.strip()), 1))
        for col in columns
    ]

    def comparer(left, right):
        comparer_iter = (compare(fn(left), fn(right)) * mult for fn, mult in comparers)
        return next((result for result in comparer_iter if result), 0)

    return sorted(items, key=cmp_to_key(comparer))

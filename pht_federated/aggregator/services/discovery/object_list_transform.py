from pht_federated.aggregator.schemas.dataset_statistics import *
from operator import itemgetter as i
from functools import cmp_to_key
from pht_federated.aggregator.services.discovery import statistics


def object_to_list(dataset_statistics_object: DatasetStatistics) -> list:

    object_list_int = []

    stats_dict = dataset_statistics_object.dict()

    #print("Dataset Statistics Object : {}".format(stats_dict))

    if "item_count" in stats_dict:
        object_list_int.append(stats_dict["item_count"])

    if "feature_count" in stats_dict:
        object_list_int.append(stats_dict["feature_count"])

    stats_columns = stats_dict["column_information"]
    #print("Stats column information : {} + type : {}".format(stats_columns, type(stats_columns)))

    stats_columns_sorted = multikeysort(stats_columns, ["type", "title"])
    #print("Stats column sorted : {}".format(stats_columns_sorted))

    for column in stats_columns_sorted:
        if column["type"] == "categorical":
            if "not_na_elements" in column:
                object_list_int.append(column["not_na_elements"])
            if "number_categories" in column:
                object_list_int.append(column["number_categories"])
            if "frequency" in column:
                object_list_int.append(column["frequency"])
        elif column["type"] == "numeric":
            if "not_na_elements" in column:
                object_list_int.append(column["not_na_elements"])
            if "mean" in column:
                object_list_int.append(column["mean"])
            if "std" in column:
                object_list_int.append(column["std"])
            if "min" in column:
                object_list_int.append(column["min"])
            if "max" in column:
                object_list_int.append(column["max"])
        elif column["type"] == "unique":
            if "number_of_duplicates" in column:
                object_list_int.append(column["number_of_duplicates"])
        elif column["type"] == "equal":
            if "value" in column:
                object_list_int.append(column["value"])
        elif column["type"] == "unstructured":
            if "not_na_elements" in column:
                object_list_int.append(column["not_na_elements"])
            if "number_targets" in column:
                object_list_int.append(column["number_targets"])
            if "frequency" in column:
                object_list_int.append(column["frequency"])



    return object_list_int


def list_to_object(dataset_statistics_list: list, dataset_statistics_object: DatasetStatistics) -> DatasetStatistics:

    stats_dict = dataset_statistics_object.dict()

    #print("Dataset Statistics Object : {}".format(stats_dict))

    if "item_count" in stats_dict:
        stats_dict["item_count"] = dataset_statistics_list[0]
    if "feature_count" in stats_dict:
        stats_dict["feature_count"] = dataset_statistics_list[1]

    dataset_statistics_list = dataset_statistics_list[2:]

    stats_columns = stats_dict["column_information"]
    stats_columns_sorted = multikeysort(stats_columns, ["type", "title"])

    for column in stats_columns_sorted:
        if column["type"] == "categorical":
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
        elif column["type"] == "numeric":
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
        elif column["type"] == "unique":
            if "number_of_duplicates":
                column["number_of_duplicates"] = dataset_statistics_list.pop(0)
        elif column["type"] == "equal":
            if "title" in column:
                None
            if "value" in column:
                del column["value"]
        elif column["type"] == "unstructured":
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


    stats_dict["column_information"] = stats_columns_sorted

    stats_dict["column_information"] = [{k:int(v) if type(v) != str else v for k,v in d.items()} for d in stats_dict["column_information"]]

    dataset_statistics_object = DatasetStatistics(**stats_dict)

    return dataset_statistics_object




def compare(x, y):
    return (x > y) - (x < y)

def multikeysort(items, columns):
    comparers = [
        ((i(col[1:].strip()), -1) if col.startswith('-') else (i(col.strip()), 1))
        for col in columns
    ]
    def comparer(left, right):
        comparer_iter = (
            compare(fn(left), fn(right)) * mult
            for fn, mult in comparers
        )
        return next((result for result in comparer_iter if result), 0)
    return sorted(items, key=cmp_to_key(comparer))


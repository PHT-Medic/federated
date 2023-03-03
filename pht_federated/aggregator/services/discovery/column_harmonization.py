from typing import List, Tuple
from fuzzywuzzy import fuzz
from pht_federated.aggregator.schemas.dataset_statistics import *
import logging


def compare_objects(object_list: List[DatasetStatistics]):
    """
    :type listOfObjects: list<Object>
    """
    logging.getLogger().setLevel(logging.INFO)

    intersection_keys = []
    difference_keys = []

    for x in range(len(object_list[:-1])):
        stats_dict = object_list[x].dict()
        stats_dict2 = object_list[x+1].dict()

        stats_dict = stats_dict["column_information"]
        stats_dict2 = stats_dict2["column_information"]

        stats_dict_filtered = filter_none_values(stats_dict)
        stats_dict2_filtered = filter_none_values(stats_dict2)

        stats_dict_keys = [list(x.keys()) for x in stats_dict_filtered]
        stats_dict_keys = set([x for l in stats_dict_keys for x in l])

        stats_dict2_keys = [list(x.keys()) for x in stats_dict2_filtered]
        stats_dict2_keys = set([x for l in stats_dict2_keys for x in l])

        # find intersection
        intersection = [x for x in stats_dict_keys if x in stats_dict2_keys]
        logging.info("Intersection between object {} and {} of list: {} ".format(x, x+1, intersection))

        # find difference (a - b)
        diff1 = list(set(stats_dict_keys).difference(set(stats_dict2_keys)))
        #logging.info("Difference between object {} - object {} of list: {}".format(x, x+1, diff1))

        # find difference (b - a)
        diff2 = list(set(stats_dict2_keys).difference(set(stats_dict_keys)))
        #logging.info("Difference between object {} - object {} of list: {}".format(x+1, x, diff2))

        logging.info("Difference between object {} - object {} of list: {}".format(x+1, x, diff1 + diff2))

        intersection_keys.append(intersection)
        difference_keys.append(diff1 + diff2)


    intersection_keys = list(set(intersection_keys[0]).intersection(*intersection_keys[1:]))
    logging.info("Intersection Keys : {}".format(intersection_keys))

    difference_keys = list(set([x for l in difference_keys for x in l]))
    logging.info("Difference Keys : {}".format(difference_keys))



def compare_two_objects(dataset_statistics: Tuple[DatasetStatistics, str], aggregator_statistics: DatasetStatistics):

    dataset_name = dataset_statistics[1]
    df_stats_dict = dataset_statistics[0].dict()
    aggregator_stats_dict = aggregator_statistics.dict()

    df_stats_dict = df_stats_dict["column_information"]
    aggregator_stats_dict = aggregator_stats_dict["column_information"]

    df_stats_dict_keys = [(x["title"], x["type"]) for x in df_stats_dict]
    aggregator_stats_dict_keys = [(x["title"], x["type"]) for x in aggregator_stats_dict]

    # find intersection
    intersection, type_differences, aggregator_keys_updated, df_stats_dict_keys = intersection_two_lists(df_stats_dict_keys, aggregator_stats_dict_keys)
    #print("Intersection between Dataset and Aggregator-Dataset: {} ".format(intersection))
    #print("Type differences between Dataset and Aggregator-Dataset: {} ".format(type_differences))

    # find difference (Dataframe - Aggregator)
    column_value_differences = list(set(df_stats_dict_keys).difference(set(aggregator_keys_updated)))
    df_stats_dict_keys, column_value_differences, matched_column_names = fuzzy_matching_prob(df_stats_dict_keys, aggregator_keys_updated, column_value_differences)
    #print("Fuzz matched columns : {}".format(matched_column_names))

    # find difference (Aggregator - Dataframe)
    column_value_differences2 = list(set(aggregator_keys_updated).difference(set(df_stats_dict_keys)))

    difference_report = create_difference_report(type_differences, column_value_differences, column_value_differences2,
                                                 matched_column_names, dataset_name)
    print("small change")

    return difference_report

def create_difference_report(type_differences: List[List[Tuple[str, str]]], column_value_differences: List[Tuple[str, str]],
                             column_value_differences2: List[Tuple[str, str]],
                             column_name_differences: List[List[Tuple[str, str]]], dataset_name: str):

    mismatch_errors_list = []

    difference_report = {
                    "dataset": dataset_name,
                    "datatype": "tabular",
                    "status": "",
                    "errors": []
    }

    for diff in type_differences:
        case = {
                 "column_name": diff[0][0],
                 "error": {
                     "type": "type",  # missing, type, semantic, extra
                     "dataframe_type": diff[0][1],
                     "aggregator_type": diff[1][1],
                 },
                 "hint": f"Change type to {diff[1][1]}",
             }
        mismatch_errors_list.append(case)

    for diff in column_value_differences:
        case = {
                 "column_name": diff[0],
                 "error": {
                     "type": "added",  # missing, type, semantic, extra
                     "dataframe_type": diff[1],
                 },
                 "hint": f"Column name {diff[0]} only exists in local dataset",
             }
        mismatch_errors_list.append(case)

    for diff in column_value_differences2:
        case = {
                 "column_name": diff[0],
                 "error": {
                     "type": "missing",  # missing, type, semantic, extra
                     "aggregator_type": diff[1],
                 },
                 "hint": f"Column name {diff[0]} only exists in aggregator dataset",
             }
        mismatch_errors_list.append(case)

    for diff in column_name_differences:
        case = {
                 "column_name": diff[0][0],
                 "error": {
                     "type": "added",  # missing, type, semantic, extra
                     "dataset_name": diff[0][0],
                     "aggregator_name": diff[1][0],
                     "aggregator_type": diff[1][1]
                 },
                 "hint": f"Column name {diff[0][0]} only exists in local dataset."
                         f" Did you mean column name: {diff[1][0]}",
             }
        mismatch_errors_list.append(case)

    if len(mismatch_errors_list) == 0:
        difference_report["status"] = "passed"
    else:
        difference_report["status"] = "failed"

    difference_report["errors"] = mismatch_errors_list

    return difference_report


def intersection_two_lists(df_stats_dict_keys: List[Tuple[str, str]], aggregator_stats_dict_keys: List[Tuple[str, str]]):

    intersection = []
    type_difference = []

    for stats_keys in df_stats_dict_keys:
        for aggregator_keys in aggregator_stats_dict_keys:
            if stats_keys == aggregator_keys:
                intersection.append(stats_keys)
            elif stats_keys[0] == aggregator_keys[0] and stats_keys[1] != aggregator_keys[1]:
                type_difference.append([stats_keys, aggregator_keys])
                aggregator_stats_dict_keys.remove(aggregator_keys)
                df_stats_dict_keys.remove(stats_keys)

    return intersection, type_difference, aggregator_stats_dict_keys, df_stats_dict_keys


def fuzzy_matching_prob(df_stats_dict_keys: List[Tuple[str, str]], aggregator_col_names: List[Tuple[str, str]],
                        difference_list: List[Tuple[str, str]]):

    matched_columns = []

    for diff in difference_list:
        for col_name in aggregator_col_names:
            ratio = fuzz.ratio(diff[0].lower(), col_name[0].lower())
            if ratio > 80:
                matched_columns.append([col_name, diff, ratio])
                #print("Difference name : {} + aggregator name : {} + matching ratio : {}".format(diff, col_name, ratio))
                difference_list = [i for i in difference_list if i != diff]
                df_stats_dict_keys = [(keys[0].replace(diff[0], col_name[0]), keys[1]) for keys in df_stats_dict_keys]

    return df_stats_dict_keys, difference_list, matched_columns


def filter_none_values(column_list: list):

    filtered_list = []

    for stats_dict in column_list:
        filtered_object = {k: v for k, v in stats_dict.items() if v is not None}
        filtered_list.append(filtered_object)

    return filtered_list



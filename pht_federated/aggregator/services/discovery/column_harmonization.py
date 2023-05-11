from typing import List, Tuple

from thefuzz import fuzz

from pht_federated.aggregator.schemas.dataset_statistics import DatasetStatistics
from pht_federated.aggregator.schemas.difference_report import *

def compare_two_datasets(
    dataset_statistics: DatasetStatistics,
    aggregator_statistics: DatasetStatistics,
    dataset_name: str,
) -> dict:
    """
    Compares two datasets in form of DatasetStatistics objects with respect to their column names
    :param dataset_statistics: DatasetStatistics of local dataset
    :param aggregator_statistics: DatasetStatistics of aggregator dataset
    :param dataset_name: Specified name of local dataset
    :return: Dictionary which lists the differences between the two datasets
    """

    input_column_information = dataset_statistics.dict()["column_information"]
    aggregator_column_information = aggregator_statistics.dict()["column_information"]

    input_column_information = [
        (x["title"], x["type"]) for x in input_column_information
    ]
    aggregator_column_information = [
        (x["title"], x["type"]) for x in aggregator_column_information
    ]

    # find intersection
    list_intersection_report = intersection_two_lists(input_column_information, aggregator_column_information)

    # find difference (Dataframe - Aggregator)
    value_differences_dataframe = list(
        set(list_intersection_report.dataframe_columns).difference(set(list_intersection_report.aggregator_columns))
    )
    (
        list_intersection_report,
        value_differences_dataframe,
        matched_column_names,
    ) = fuzzy_matching_prob(
        list_intersection_report,
        value_differences_dataframe,
        80,
    )

    # find difference (Aggregator - Dataframe)
    value_differences_aggregator = list(
        set(list_intersection_report.aggregator_columns).difference(set(list_intersection_report.dataframe_columns))
    )

    difference_report_requirements = {
        "type_differences": list_intersection_report.type_differences,
        "dataframe_value_difference": value_differences_dataframe,
        "aggregator_value_difference": value_differences_aggregator,
        "matched_column_names": matched_column_names,
        "dataset_name": dataset_name
    }

    difference_report_requirements = DifferenceReportRequirements(**difference_report_requirements)

    difference_report = create_difference_report(
        difference_report_requirements
    )

    return difference_report


def create_difference_report(
difference_report_requirements: DifferenceReportRequirements
) -> dict:
    """
    Transforms multiple types of mismatch errors between datasets into a summarized difference report
    :param type_differences: Lists differences in type
    :param value_differences_dataframe: Lists differences (Dataframe - Aggregator)
    :param value_differences_aggregator: Lists differences (Aggregator - Dataframe)
    :param name_differences: Lists differences in name only
    :param dataset_name: String that defines the name of local dataset
    :return: Dictionary which lists the differences between the two datasets
    """


    difference_report = {
        "dataset": difference_report_requirements.dataset_name,
        "datatype": "tabular",
        "status": "",
        "errors": [],
    }

    # adds errors to difference report where there is a difference in the type of the same column_name
    for diff in difference_report_requirements.type_differences:
        case = {
            "column_name": diff[0][0],
            "error": {
                "type": "type",  # missing, type, semantic, extra
                "dataframe_type": diff[0][1],
                "aggregator_type": diff[1][1],
            },
            "hint": f'Change type of column "{diff[0][0]}" to "{diff[1][1]}"',
        }
        difference_report["errors"].append(case)

    # adds errors to difference report where column_names only exist in local dataset
    for diff in difference_report_requirements.dataframe_value_difference:
        case = {
            "column_name": diff[1],
            "error": {
                "type": "added",  # missing, type, semantic, extra
                "dataframe_type": diff[0],
            },
            "hint": f'Column name "{diff[1]}" only exists in local dataset',
        }
        difference_report["errors"].append(case)

    # adds errors to difference report where column_names only exist in aggregator
    for diff in difference_report_requirements.aggregator_value_difference:
        case = {
            "column_name": diff[0],
            "error": {
                "type": "missing",  # missing, type, semantic, extra
                "aggregator_type": diff[1],
            },
            "hint": f'Column name "{diff[0]}" only exists in aggregator dataset',
        }
        difference_report["errors"].append(case)

    # adds errors to difference report where column names between datasets mismatch but similarity is significant
    for diff in difference_report_requirements.matched_column_names:
        case = {
            "column_name": diff[1][0],
            "error": {
                "type": "added",  # missing, type, semantic, extra
                "dataset_name": diff[1][0],
                "aggregator_name": diff[0][0],
                "aggregator_type": diff[1][1],
            },
            "hint": f'Column name "{diff[1][0]}" only exists in local dataset.'
            f' Did you mean column name: "{diff[0][0]}"',
        }
        difference_report["errors"].append(case)

    if len(difference_report["errors"]) == 0:
        difference_report["status"] = "passed"
    else:
        difference_report["status"] = "failed"

    return difference_report


def intersection_two_lists(
    df_col_names: List[Tuple[str, str]],
    aggregator_col_names: List[Tuple[str, str]],
):
    """
    Compares the column_names and types of the local dataset and the aggregated dataset and returns the intersection
    between both
    :param df_col_names: Lists column_names & types of local dataset
    :param aggregator_col_names: Lists column_names & types of aggregator dataset
    :return: intersection -> Lists column_names & types of identical columns between local dataset & aggregator dataset
    :return: type_differences -> Lists differences between local dataset and aggregator dataset if only type mismatches
    :return: aggregator_col_names -> Updated list that removed columns with type differences
    :return: df_col_names -> Updated list that removed columns with type differences
    """

    intersection = []
    type_differences = []

    for stats_keys in df_col_names:
        for aggregator_keys in aggregator_col_names:
            if stats_keys == aggregator_keys:
                intersection.append(stats_keys)
            elif (
                stats_keys[0] == aggregator_keys[0]
                and stats_keys[1] != aggregator_keys[1]
            ):
                if [stats_keys, aggregator_keys] not in type_differences:
                    type_differences.append([stats_keys, aggregator_keys])

    for tup in type_differences:
        aggregator_col_names.remove(tup[1])
        df_col_names.remove(tup[0])

    list_intersection_report = {
        "intersection": intersection,
        "type_differences": type_differences,
        "dataframe_columns": df_col_names,
        "aggregator_columns": aggregator_col_names
    }

    list_intersection_report = ListIntersectionReport(**list_intersection_report)


    return  list_intersection_report


def fuzzy_matching_prob(
    list_intersection_report: ListIntersectionReport,
    difference_list: List[Tuple[str, str]],
    matching_probability_threshold: int,
):
    """
    Checks whether the name-differences between the two datasets might be due to typing and not semantic nature.
    Applies fuzzy matching to check the Levenshtein distance between the column names to find matches.
    :param list_intersection_report: Lists column_names & types of identical columns between local dataset & aggregator dataset
    :param difference_list: Lists differences in column names
    :param matching_probability_threshold: Threshold probability when two column names are recognized as a match
    :return: list_intersection_report -> Updated object to not include different column_names
    :return: difference_list -> Updated list if matching was successfull
    :return matched_columns -> Matches get added to list if matching probability > 80
    """

    matched_columns = []

    for diff in difference_list:
        for col_name in list_intersection_report.aggregator_columns:
            ratio = fuzz.ratio(diff[0].lower(), col_name[0].lower())
            if ratio > matching_probability_threshold:
                matched_columns.append([col_name, diff, ratio])
                difference_list = [i for i in difference_list if i != diff]
                list_intersection_report.dataframe_columns = [
                    (keys[0].replace(diff[0], col_name[0]), keys[1])
                    for keys in list_intersection_report.dataframe_columns
                ]



    return list_intersection_report, difference_list, matched_columns

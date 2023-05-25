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
        DataframeColumn(**{"name": x["title"], "type": x["type"]}) for x in input_column_information
    ]
    aggregator_column_information = [
        AggregatorColumn(**{"name": x["title"], "type": x["type"]}) for x in aggregator_column_information
    ]

    # find intersection
    list_intersection_report = intersection_two_lists(
        input_column_information, aggregator_column_information
    )

    print("List intersection report dataframe columns : {}".format(list_intersection_report.dataframe_columns))
    print("List intersection report aggregator columns : {}".format(list_intersection_report.aggregator_columns))

    # find difference (Dataframe - Aggregator)
    value_differences_dataframe = []
    for col in list_intersection_report.dataframe_columns:
        count = 0
        for col2 in list_intersection_report.aggregator_columns:
            if not (col.name == col2.name and col.type == col2.type) and count == 0:
                value_differences_dataframe.append(col)
                count += 1

    print("Value differences dataframe : {}".format(value_differences_dataframe))

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
        set(list_intersection_report.aggregator_columns).difference(
            set(list_intersection_report.dataframe_columns)
        )
    )

    difference_report_requirements = {
        "type_differences": list_intersection_report.type_differences,
        "dataframe_value_difference": value_differences_dataframe,
        "aggregator_value_difference": value_differences_aggregator,
        "matched_column_names": matched_column_names,
        "dataset_name": dataset_name,
    }

    print("List intersection type differences : {}".format(list_intersection_report.type_differences))
    print("dataframe value differences : {}".format(value_differences_dataframe))
    print("aggregator value differences : {}".format(value_differences_aggregator))
    print("matched column names : {}".format(matched_column_names))

    difference_report_requirements = DifferenceReportRequirements(
        **difference_report_requirements
    )

    difference_report = create_difference_report(difference_report_requirements)

    return difference_report


def create_difference_report(
    difference_report_requirements: DifferenceReportRequirements,
) -> DifferenceReportBackend:
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
            "error_type": "type",  # missing, type, semantic, extra
            "column_name": diff[0][0],
            "dataframe_type": diff[0][1],
            "aggregator_type": diff[1][1],
            "hint": f'Change type of column "{diff[0][0]}" to "{diff[1][1]}"',
        }
        difference_report["errors"].append(case)

    # adds errors to difference report where column_names only exist in local dataset
    for diff in difference_report_requirements.dataframe_value_difference:
        case = {
            "error_type": "added",  # missing, type, semantic, extra
            "column_name": diff[1],
            "dataframe_type": diff[0],
            "hint": f'Column name "{diff[1]}" only exists in local dataset',
        }
        difference_report["errors"].append(case)

    # adds errors to difference report where column_names only exist in aggregator
    for diff in difference_report_requirements.aggregator_value_difference:
        case = {
            "error_type": "missing",  # missing, type, semantic, extra
            "column_name": diff[0],
            "aggregator_type": diff[1],
            "hint": f'Column name "{diff[0]}" only exists in aggregator dataset',
        }
        difference_report["errors"].append(case)

    # adds errors to difference report where column names between datasets mismatch but similarity is significant
    for diff in difference_report_requirements.matched_column_names:
        case = {
            "error_type": "added_name",  # missing, type, semantic, extra
            "column_name": diff[1][0],
            "dataframe_name": diff[1][0],
            "aggregator_name": diff[0][0],
            "aggregator_type": diff[1][1],
            "hint": f'Column name "{diff[1][0]}" only exists in local dataset.'
            f' Did you mean column name: "{diff[0][0]}"',
        }
        difference_report["errors"].append(case)

    if len(difference_report["errors"]) == 0:
        difference_report["status"] = "passed"
    else:
        difference_report["status"] = "failed"

    difference_report = DifferenceReportBackend(**difference_report)

    return difference_report


def intersection_two_lists(
    df_col_names: List[DataframeColumn],
    aggregator_col_names: List[AggregatorColumn],
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

    for dataframe_column in df_col_names:
        for aggregator_column in aggregator_col_names:
            if dataframe_column.name == aggregator_column.name and dataframe_column.type == aggregator_column.type:
                intersection.append(dataframe_column)
            elif (
                dataframe_column.name == aggregator_column.name
                and dataframe_column.type != aggregator_column.type
            ):
                value_type_differences = VariableTypeDifference(**{
                    "local_column_name": dataframe_column.name,
                    "aggregator_column_name": aggregator_column.name,
                    "local_column_type": dataframe_column.type,
                    "aggregator_column_type": aggregator_column.type
                })
                if value_type_differences not in type_differences:
                    type_differences.append(value_type_differences)


    for diff in type_differences:
        for col in aggregator_col_names:
            if diff.aggregator_column_name == col.name and diff.aggregator_column_type == col.type:
                aggregator_col_names.remove(col)
        for col in df_col_names:
            if diff.local_column_name == col.name and diff.local_column_type == col.type:
                df_col_names.remove(col)

    list_intersection_report = {
        "intersection": intersection,
        "type_differences": type_differences,
        "dataframe_columns": df_col_names,
        "aggregator_columns": aggregator_col_names,
    }

    list_intersection_report = ListIntersectionReport(**list_intersection_report)

    return list_intersection_report


def fuzzy_matching_prob(
    list_intersection_report: ListIntersectionReport,
    difference_list: List[DataframeColumn],
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

    print("Difference list: {} ".format(difference_list))
    print("Aggregator columns: {} ".format(list_intersection_report.aggregator_columns))

    for diff in difference_list:
        for col in list_intersection_report.aggregator_columns:
            print("Diff: {} ".format(diff.name.lower()))
            print("Col: {} ".format(col.name.lower()))
            ratio = fuzz.ratio(diff.name.lower(), col.name.lower())
            if ratio > matching_probability_threshold:
                matched_columns.append(MatchedColumnNames(**{
                                                          "local_column_name": diff.name,
                                                          "aggregator_column_name": col.name,
                                                          "matching_probability": ratio}))

                difference_list = [i for i in difference_list if i.name != diff.name]

                for c in range(len(list_intersection_report.dataframe_columns)):
                    list_intersection_report.dataframe_columns[c].name = col.name

    print("Matched columns: {} ".format(matched_columns))
    return list_intersection_report, difference_list, matched_columns

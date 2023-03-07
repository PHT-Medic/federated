from typing import List, Tuple

from fuzzywuzzy import fuzz

from pht_federated.aggregator.schemas.dataset_statistics import DatasetStatistics


def compare_two_datasets(
    dataset_statistics: Tuple[DatasetStatistics, str],
    aggregator_statistics: DatasetStatistics,
) -> dict:
    """
    Compares two datasets in form of DatasetStatistics objects with respect to their column names
    :param dataset_statistics: DatasetStatistics of local dataset
    :param aggregator_statistics: DatasetStatistics of aggregator dataset
    :return: Dictionary which lists the differences between the two datasets
    """

    dataset_name = dataset_statistics[1]
    df_stats_dict = dataset_statistics[0].dict()
    aggregator_stats_dict = aggregator_statistics.dict()

    df_stats_dict = df_stats_dict["column_information"]
    aggregator_stats_dict = aggregator_stats_dict["column_information"]

    df_stats_dict_keys = [(x["title"], x["type"]) for x in df_stats_dict]
    aggregator_stats_dict_keys = [
        (x["title"], x["type"]) for x in aggregator_stats_dict
    ]

    # find intersection
    (
        intersection,
        type_differences,
        aggregator_keys_updated,
        df_stats_dict_keys,
    ) = intersection_two_lists(df_stats_dict_keys, aggregator_stats_dict_keys)

    # find difference (Dataframe - Aggregator)
    column_value_differences = list(
        set(df_stats_dict_keys).difference(set(aggregator_keys_updated))
    )
    (
        df_stats_dict_keys,
        column_value_differences,
        matched_column_names,
    ) = fuzzy_matching_prob(
        df_stats_dict_keys, aggregator_keys_updated, column_value_differences
    )

    # find difference (Aggregator - Dataframe)
    column_value_differences2 = list(
        set(aggregator_keys_updated).difference(set(df_stats_dict_keys))
    )

    difference_report = create_difference_report(
        type_differences,
        column_value_differences,
        column_value_differences2,
        matched_column_names,
        dataset_name,
    )

    return difference_report


def create_difference_report(
    type_differences: List[List[Tuple[str, str]]],
    column_value_differences: List[Tuple[str, str]],
    column_value_differences2: List[Tuple[str, str]],
    column_name_differences: List[List[Tuple[str, str]]],
    dataset_name: str,
) -> dict:
    """
    Transforms multiple types of mismatch errors between datasets into a summarized difference report
    :param type_differences: List[List[Tuple[col_name_df, type], Tuple[col_name_aggregator, type]]] differences in type
    :param column_value_differences: List[Tuple[col_name, type]] differences (Dataframe - Aggregator)
    :param column_value_differences2: List[Tuple[col_name, type]] differences (Aggregator - Dataframe)
    :param column_name_differences: List[List[Tuple[col_name_df, type], Tuple[col_name_aggregator, type]]] differences
                                    in name only
    :param dataset_name: String that defines the name of local dataset
    :return: Dictionary which lists the differences between the two datasets
    """

    mismatch_errors_list = []

    difference_report = {
        "dataset": dataset_name,
        "datatype": "tabular",
        "status": "",
        "errors": [],
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
                "aggregator_type": diff[1][1],
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


def intersection_two_lists(
    df_col_names: List[Tuple[str, str]],
    aggregator_col_names: List[Tuple[str, str]],
):
    """
    Compares the column_names and types of the local dataset and the aggregated dataset and returns the intersection
    between both
    :param df_col_names: List[Tuple[col_name, type]]
    :param aggregator_col_names: List[Tuple[col_name, type]]
    :return: intersection -> List[Tuple[col_name, type]] lists column_names & types of identical columns between
                             local dataset and aggregator dataset
    :return: type_differences -> List[List[Tuple[col_name_df, type], Tuple[col_name_aggregator, type]]] lists
                                 differences between local dataset and aggregator dataset if only type mismatches
    :return: aggregator_col_names -> List[Tuple[col_name, type]] updated list that removed columns with type differences
    :return: df_col_names -> List[Tuple[col_name, type]] updated list that removed columns with type differences
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
                type_differences.append([stats_keys, aggregator_keys])
                aggregator_col_names.remove(aggregator_keys)
                df_col_names.remove(stats_keys)

    return intersection, type_differences, aggregator_col_names, df_col_names


def fuzzy_matching_prob(
    df_col_names: List[Tuple[str, str]],
    aggregator_col_names: List[Tuple[str, str]],
    difference_list: List[Tuple[str, str]],
):
    """
    Checks whether the name-differences between the two datasets might be due to typing and not semantic nature.
    Applies fuzzy matching to check the Levenshtein distance between the column names to find matches.
    :param df_col_names: List[Tuple[col_name, type]]
    :param aggregator_col_names: List[Tuple[col_name, type]]
    :param difference_list: List[Tuple[col_name, type]] which lists differences in column names
    :return: df_col_names -> List[Tuple[col_name, type]] updated to not conclude different column_names
    :return: difference_list -> List[Tuple[col_name, type]] updated if matching was successfull
    :return matched_columns -> List[List[col_name_df, col_name_aggregator, matching_ratio]] matches get added if
                               matching probability > 80
    """

    matched_columns = []

    for diff in difference_list:
        for col_name in aggregator_col_names:
            ratio = fuzz.ratio(diff[0].lower(), col_name[0].lower())
            if ratio > 80:
                matched_columns.append([col_name, diff, ratio])
                difference_list = [i for i in difference_list if i != diff]
                df_col_names = [
                    (keys[0].replace(diff[0], col_name[0]), keys[1])
                    for keys in df_col_names
                ]

    return df_col_names, difference_list, matched_columns

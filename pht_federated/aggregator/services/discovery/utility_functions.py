import json
from collections import Counter
from typing import Union

import plotly.io
from fastapi.encoders import jsonable_encoder

from pht_federated.aggregator.schemas.discovery import DiscoverySummary
from pht_federated.aggregator.schemas.figures import DiscoveryFigure
from pht_federated.aggregator.services.discovery.plots import (
    create_barplot,
    create_dot_plot,
)
from pht_federated.aggregator.services.discovery.statistics import calc_combined_std


def aggregate_proposal_features(
    response: list, proposal_id: str, features: Union[str, None]
) -> DiscoverySummary:
    """
    Aggregates the individual values of >= 2 DatasetStatistics objects
    :param response: list of DatasetStatistics objects
    :param proposal_id: integer value of the corresponding proposal
    :param query: comma seperated list that specifies feature parameter that should be aggregated
    :return: DiscoverySummary object
    """

    feature_lst = []
    aggregated_feature_lst = []
    discovery_item_count = 0
    discovery_feature_count = 0

    if len(response) < 2:
        raise ValueError(
            "Not able to aggregate a discovery summary over less than 2 DatasetStatistics. Aborted."
        )
    else:
        for discovery in response:
            discovery = jsonable_encoder(discovery)
            discovery_item_count += discovery["item_count"]
            discovery_feature_count += discovery["feature_count"]

            for feature in discovery["column_information"]:
                if features:
                    selected_features = features.split(",")
                    if feature["title"] in selected_features:
                        feature_lst.append(feature)
                else:
                    feature_lst.append(feature)

        for feature in feature_lst:
            if feature["type"] == "numeric":
                discovery_summary_json = aggregate_numerical_columns(
                    feature_lst, feature
                )
                aggregated_feature_lst.append(discovery_summary_json)

            elif feature["type"] == "categorical":
                discovery_summary_json = aggregate_categorical_columns(
                    feature_lst, feature, len(response)
                )
                aggregated_feature_lst.append(discovery_summary_json)

            elif feature["type"] == "unstructured":
                discovery_summary_json = aggregate_unstructured_data(
                    feature_lst, feature
                )
                aggregated_feature_lst.append(discovery_summary_json)

            elif feature["type"] == "unique":
                discovery_summary_json = aggregate_unique_columns(
                    feature_lst, feature, len(response)
                )
                aggregated_feature_lst.append(discovery_summary_json)

            elif feature["type"] == "equal":
                discovery_summary_json = aggregate_equal_columns(feature_lst, feature)
                aggregated_feature_lst.append(discovery_summary_json)

            feature_lst = [x for x in feature_lst if x["title"] != feature["title"]]

            if len(feature_lst) == 0:
                break

        discovery_feature_count /= len(response)

        discovery_summary_schema = {
            "proposal_id": proposal_id,
            "item_count": discovery_item_count,
            "feature_count": discovery_feature_count,
            "column_information": aggregated_feature_lst,
        }
        discovery_summary = DiscoverySummary(**discovery_summary_schema)

    return discovery_summary


def aggregate_numerical_columns(feature_lst: list, feature: dict) -> dict:
    """
    Aggregates the values of a numerical feature column as part of DatasetStatistics object
    :param feature_lst: list of features that are supposed to be aggregated
    :param feature: specific feature which values get aggregated over available DatasetStatistics objects
    :return: part of column_information of DiscoverySummary object
    """
    discovery_title = ""
    discovery_item_count_not_na = []
    discovery_mean = []
    discovery_std = []
    discovery_min = []
    discovery_max = []

    for feature_duplicate in feature_lst:
        if feature_duplicate["title"] == feature["title"]:
            data = feature_duplicate
            discovery_title = data["title"]
            discovery_item_count_not_na.append(data["not_na_elements"])
            discovery_mean.append(
                (data["mean"], data["mean"] * data["not_na_elements"])
            )
            discovery_std.append(data["std"])
            discovery_min.append(data["min"])
            discovery_max.append(data["max"])

    discovery_mean_combined = sum([pair[1] for pair in discovery_mean]) / sum(
        discovery_item_count_not_na
    )
    discovery_std = calc_combined_std(
        discovery_item_count_not_na,
        discovery_std,
        discovery_mean,
        discovery_mean_combined,
    )
    discovery_min = min(discovery_min)
    discovery_max = max(discovery_max)

    discovery_summary_json = {
        "type": "numeric",
        "title": discovery_title,
        "not_na_elements": sum(discovery_item_count_not_na),
        "mean": discovery_mean_combined,
        "std": discovery_std,
        "min": discovery_min,
        "max": discovery_max,
    }

    figure = create_dot_plot(discovery_summary_json)
    fig_json = plotly.io.to_json(figure)
    obj = json.loads(fig_json)

    figure_schema = {"title": discovery_title, "type": "numeric", "figure": obj}

    discovery_figure = DiscoveryFigure(**figure_schema)
    discovery_summary_json["figure_data"] = discovery_figure

    return discovery_summary_json


def aggregate_categorical_columns(
    feature_lst: list, feature: dict, num_discoveries: int
) -> dict:
    """
    Aggregates the values of a categorical feature column as part of DatasetStatistics object
    :param feature_lst: list of features that are supposed to be aggregated
    :param feature: specific feature which values get aggregated over available DatasetStatistics objects
    :return: part of column_information of DiscoverySummary object
    """
    discovery_title = ""
    discovery_item_count_not_na = []
    discovery_number_categories = 0
    discovery_value_counts = []

    for feature_duplicate in feature_lst:
        if feature_duplicate["title"] == feature["title"]:
            data = feature_duplicate

            discovery_title = data["title"]
            discovery_item_count_not_na.append(data["not_na_elements"])
            discovery_number_categories += data["number_categories"]
            discovery_value_counts.append(data["value_counts"])

    c = Counter()
    for d in discovery_value_counts:
        c.update(d)

    discovery_value_counts = dict(c)
    # for entry in discovery_value_counts.items():
    #    discovery_value_counts[entry[0]] = round(entry[1] / num_discoveries)

    discovery_most_frequent_element = max(
        discovery_value_counts, key=discovery_value_counts.get
    )
    discovery_frequency = discovery_value_counts[discovery_most_frequent_element]
    discovery_number_categories /= num_discoveries

    discovery_summary_json = {
        "type": "categorical",
        "title": discovery_title,
        "not_na_elements": sum(discovery_item_count_not_na),
        "number_categories": discovery_number_categories,
        "most_frequent_element": discovery_most_frequent_element,
        "frequency": discovery_frequency,
        "value_counts": discovery_value_counts,
    }

    figure = create_barplot(discovery_summary_json)
    fig_json = plotly.io.to_json(figure)
    obj = json.loads(fig_json)

    figure_schema = {"title": discovery_title, "type": "numeric", "figure": obj}

    discovery_figure = DiscoveryFigure(**figure_schema)
    discovery_summary_json["figure_data"] = discovery_figure

    return discovery_summary_json


def aggregate_unstructured_data(feature_lst: list, feature: dict):
    discovery_summary_json = {"type": "unstructured"}

    return discovery_summary_json


def aggregate_unique_columns(feature_lst: list, feature: dict, num_discoveries: int):
    """
    Aggregates the values a unique feature column as part of DatasetStatistics object
    :param feature_lst: list of features that are supposed to be aggregated
    :param feature: specific feature which values get aggregated over available DatasetStatistics objects
    :return: part of column_information of DiscoverySummary object
    """
    discovery_title = ""
    discovery_no_duplicates = 0

    for feature_duplicate in feature_lst:
        if feature_duplicate["title"] == feature["title"]:
            data = feature_duplicate
            discovery_title = data["title"]
            discovery_no_duplicates += data["number_of_duplicates"]

    discovery_no_duplicates /= num_discoveries

    discovery_summary_json = {
        "type": "unique",
        "title": discovery_title,
        "number_of_duplicates": discovery_no_duplicates,
    }

    return discovery_summary_json


def aggregate_equal_columns(feature_lst: list, feature: dict):
    """
    Aggregates the values of a equal feature column as part of DatasetStatistics object
    :param feature_lst: list of features that are supposed to be aggregated
    :param feature: specific feature which values get aggregated over available DatasetStatistics objects
    :return: part of column_information of DiscoverySummary object
    """
    discovery_title = ""
    discovery_equal_value = []

    for feature_duplicate in feature_lst:
        if feature_duplicate["title"] == feature["title"]:
            data = feature_duplicate
            discovery_title = data["title"]
            discovery_equal_value.append(data["value"])

    if discovery_equal_value.count(discovery_equal_value[0]) == len(
        discovery_equal_value
    ):
        pass
    else:
        raise Exception(
            f"Not all discoveries share an equal column considering the feature {discovery_title} "
        )

    discovery_summary_json = {
        "type": "equal",
        "title": discovery_title,
        "value": discovery_equal_value[0],
    }

    return discovery_summary_json

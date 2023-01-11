import json
from collections import Counter
from typing import Union

import plotly.io
from fastapi.encoders import jsonable_encoder

from pht_federated.aggregator.schemas.discovery import DiscoverySummary, DiscoveryTabularSummary, DiscoveryCSVSummary,DiscoveryResourceSummary,DiscoveryFHIRSummary
from pht_federated.aggregator.schemas.figures import DiscoveryFigure
from pht_federated.aggregator.services.discovery.plots import (
    create_barplot,
    create_dot_plot,
)
from pht_federated.aggregator.services.discovery.statistics import calc_combined_std

def aggregate_proposal_csv_features(response: list, proposal_id: str, features: Union[str, None]):
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
            discovery_item_count += discovery["statistics"][0]["csv_statistics"]["item_count"]
            discovery_feature_count += discovery["statistics"][0]["csv_statistics"]["feature_count"]

            for feature in discovery["statistics"][0]["csv_statistics"]["column_information"]:
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

        discovery_tabular_summary_schema = {
            "item_count": discovery_item_count,
            "feature_count": discovery_feature_count,
            "column_information": aggregated_feature_lst,
        }

        discovery_tabular_summary = DiscoveryTabularSummary(**discovery_tabular_summary_schema)
        discovery_csv_summary_schema = {
            "type": "csv",
            "discovery_csv_summary": discovery_tabular_summary
        }
        discovery_csv_summary = DiscoveryCSVSummary(**discovery_csv_summary_schema)
        discovery_summary_schema = {
            "proposal_id": proposal_id,
            "summary":[discovery_csv_summary]
        }
        discovery_summary = DiscoverySummary(**discovery_summary_schema)
        return discovery_summary

def aggregate_proposal_fhir_features(response: list, proposal_id: str, features: Union[str, None]):
    total_resources_names = []
    total_resources_statistics = []

    if len(response) < 2:
        raise ValueError(
            "Not able to aggregate a discovery summary over less than 2 DatasetStatistics. Aborted."
        )
    else:
        for discovery in response:
            discovery = jsonable_encoder(discovery)
            disc_res_types = discovery["statistics"][0]["resource_types"]
            total_resources_names = list(set(total_resources_names)|set(disc_res_types))

        for resource in total_resources_names:
            number_of_resources = 0
            resource_feature_lst = []
            resource_aggregated_feature_lst = []
            discovery_resource_item_count = 0
            discovery_resource_feature_count = 0
            for discovery in response:
                discovery = jsonable_encoder(discovery)
                for res_disc in discovery["statistics"][0]["server_statistics"]:
                    if resource == res_disc["resource_name"]:
                        number_of_resources+=1
                        discovery_resource_item_count += res_disc["resource_statistics"]["item_count"]
                        discovery_resource_feature_count +=res_disc["resource_statistics"]["feature_count"]
                        for feature in res_disc["resource_statistics"]["column_information"]:
                            if features:
                                selected_features = features.split(",")
                                if feature["title"] in selected_features:
                                    resource_feature_lst.append(feature)
                            else:
                                resource_feature_lst.append(feature)

            for feature in resource_feature_lst:
                if feature["type"] == "numeric":
                    discovery_summary_json = aggregate_numerical_columns(
                        resource_feature_lst, feature
                    )
                    resource_aggregated_feature_lst.append(discovery_summary_json)

                elif feature["type"] == "categorical":
                    discovery_summary_json = aggregate_categorical_columns(
                        resource_feature_lst, feature, number_of_resources
                    )
                    resource_aggregated_feature_lst.append(discovery_summary_json)

                elif feature["type"] == "unstructured":
                    discovery_summary_json = aggregate_unstructured_data(
                        resource_feature_lst, feature
                    )
                    resource_aggregated_feature_lst.append(discovery_summary_json)

                elif feature["type"] == "unique":
                    if(resource == "Patient"):
                        print()
                    discovery_summary_json = aggregate_unique_columns(
                        resource_feature_lst, feature, number_of_resources
                    )
                    resource_aggregated_feature_lst.append(discovery_summary_json)

                elif feature["type"] == "equal":
                    discovery_summary_json = aggregate_equal_columns(resource_feature_lst, feature)
                    resource_aggregated_feature_lst.append(discovery_summary_json)

                resource_feature_lst = [x for x in resource_feature_lst if x["title"] != feature["title"]]
                if len(resource_feature_lst) == 0:
                    break

            discovery_resource_feature_count /= number_of_resources

            discovery_tabular_summary_schema = {
                "item_count": discovery_resource_item_count,
                "feature_count": discovery_resource_feature_count,
                "column_information": resource_aggregated_feature_lst,
            }
            discovery_tabular_summary = DiscoveryTabularSummary(**discovery_tabular_summary_schema)

            discovery_resource_summary_schema = {
                "resource_name": resource,
                "resource_statistics":discovery_tabular_summary
            }
            discovery_resource_summary = DiscoveryResourceSummary(**discovery_resource_summary_schema)
            print()
            total_resources_statistics.append(discovery_resource_summary)

        print(total_resources_statistics)
        discovery_fhir_summary_schema = {
            "type": "fhir",
            "discovery_resource_types":total_resources_names,
            "discovery_server_statistics": total_resources_statistics
        }
        discovery_fhir_summary = DiscoveryFHIRSummary(**discovery_fhir_summary_schema)
        discovery_summary_schema = {
            "proposal_id": proposal_id,
            "summary":[discovery_fhir_summary]
        }
        discovery_summary = DiscoverySummary(**discovery_summary_schema)
        return discovery_summary
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
    test_dataset = jsonable_encoder(response[0])
    discovery_summary = "Test"
    print()
    if test_dataset["statistics"][0]["type"] == "fhir":
        discovery_summary = aggregate_proposal_fhir_features(response,proposal_id,features)
    elif test_dataset["statistics"][0]["type"] == "csv":
        discovery_summary = aggregate_proposal_csv_features(response, proposal_id, features)
    else:
        print("Other types needs to be implemented. Only fhir and csv so far!")
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

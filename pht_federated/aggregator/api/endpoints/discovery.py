from fastapi import APIRouter, Depends, HTTPException
from fastapi.encoders import jsonable_encoder
from typing import Any, List

from pht_federated.aggregator.api.schemas.discovery import *
from pht_federated.aggregator.api.schemas.dataset_statistics import *
from pht_federated.aggregator.api.schemas.figures import DiscoveryFigure, DiscoveryFigures
from pht_federated.aggregator.api.crud.crud_discovery import discoveries
from pht_federated.aggregator.api.crud.crud_dataset_statistics import datasets
from pht_federated.aggregator.api.discoveries.statistics import *

from pht_federated.aggregator.api import dependencies
from sqlalchemy.orm import Session


router = APIRouter()

@router.get("/{proposal_id}/discovery", response_model=DiscoverySummary)
def get_discovery_all(proposal_id: int, db: Session = Depends(dependencies.get_db)):

    response = datasets.get_all_by_dataset_id(proposal_id, db)
    if not response:
        raise HTTPException(status_code=404, detail=f"Discovery of proposal with id '{proposal_id}' not found.")

    feature_lst = []
    aggregated_feature_lst = []
    discovery_item_count = 0
    discovery_feature_count = 0

    if len(response) < 2:
        print("Not able to aggregate a discovery summary over less than 2 DatasetStatistics. Aborted.")
        discovery_summary_schema = {}
        discovery_summary = DiscoverySummary(**discovery_summary_schema)
        return discovery_summary
    else:
        for discovery in response:
            discovery = jsonable_encoder(discovery)
            discovery_item_count += discovery['n_items']
            discovery_feature_count += discovery['n_features']
            for feature in discovery['column_information']:
                feature_lst.append(feature)


        for feature in feature_lst:
            if feature['type'] == 'numeric':
                value = feature

                discovery_title = ""
                discovery_item_count_not_na = 0
                discovery_mean = 0
                discovery_std = 0
                discovery_min = 0
                discovery_max = 0

                for feature2 in feature_lst:
                    if feature2['title'] == value['title']:
                        data = feature2
                        discovery_title = data['title']
                        discovery_item_count_not_na += data['not_na_elements']
                        discovery_mean += data['mean']
                        discovery_std += data['std']
                        discovery_min += data['min']
                        discovery_max += data['max']

                feature_lst = [x for x in feature_lst if x['title'] != discovery_title]

                discovery_mean /= len(response)
                discovery_std /= len(response)
                discovery_min /= len(response)
                discovery_max /= len(response)

                discovery_summary_json = {
                    "type": 'numeric',
                    "title": discovery_title,
                    "not_na_elements": discovery_item_count_not_na,
                    "mean": discovery_mean,
                    "std": discovery_std,
                    "min": discovery_min,
                    "max": discovery_max
                }

                figure = create_errorbar(discovery_summary_json)
                fig_json = plotly.io.to_json(figure)
                obj = json.loads(fig_json)

                figure_schema = {
                    'title': discovery_title,
                    'type': "numeric",
                    'figure': obj
                }

                discovery_figure = DiscoveryFigure(**figure_schema)
                discovery_summary_json['figure_data'] = discovery_figure
                aggregated_feature_lst.append(discovery_summary_json)

                if len(feature_lst) == 0:
                    break

            else:
                value = feature

                discovery_title = ""
                discovery_item_count_not_na = 0
                discovery_number_categories = 0
                discovery_most_frequent_element = ""
                discovery_frequency = 0

                for feature2 in feature_lst:
                    if feature2['title'] == value['title']:
                        data = feature2

                        discovery_title = data['title']
                        discovery_item_count_not_na += data['not_na_elements']
                        discovery_number_categories += data['number_categories']
                        discovery_frequency += data['frequency']
                        if data['frequency'] > discovery_frequency:
                            discovery_most_frequent_element = data['most_frequent_element']

                feature_lst = [x for x in feature_lst if x['title'] != discovery_title]

                discovery_number_categories /= len(response)
                discovery_frequency /= len(response)

                discovery_summary_json = {
                    "type": 'categorical',
                    "title": discovery_title,
                    "not_na_elements": discovery_item_count_not_na,
                    "number_categories": discovery_number_categories,
                    "most_frequent_element": discovery_most_frequent_element,
                    "frequency": discovery_frequency
                }

                figure = create_errorbar(discovery_summary_json)
                fig_json = plotly.io.to_json(figure)
                obj = json.loads(fig_json)

                figure_schema = {
                    'title': discovery_title,
                    'type': "numeric",
                    'figure': obj
                }

                discovery_figure = DiscoveryFigure(**figure_schema)
                discovery_summary_json['figure_data'] = discovery_figure
                aggregated_feature_lst.append(discovery_summary_json)

                if len(feature_lst) == 0:
                    break

        discovery_feature_count /= len(response)

        discovery_summary_schema = {
            "proposal_id": proposal_id,
            "item_count": discovery_item_count,
            "feature_count": discovery_feature_count,
            "data_information": aggregated_feature_lst
        }

        discovery_summary = DiscoverySummary(**discovery_summary_schema)

        print("DISCOVERY SUMMARY : {}".format(discovery_summary))

        return discovery_summary

@router.get("/{proposal_id}/discovery_feature", response_model=DiscoverySummary)
def get_discovery_single(proposal_id: int,  feature_name: str, db: Session = Depends(dependencies.get_db)):

    response = datasets.get_all_by_dataset_id(proposal_id, db)
    if not response:
        raise HTTPException(status_code=404, detail=f"Discovery of proposal with id '{proposal_id}' not found.")

    discovery_item_count = 0
    discovery_feature_count = 0
    discovery_item_count_not_na = 0
    discovery_mean = 0
    discovery_std = 0
    discovery_min = 0
    discovery_max = 0

    discovery_number_categories = 0
    discovery_most_frequent_element = ""
    discovery_frequency = 0

    feature_type = ""

    if len(response) < 2:
        print("Not able to aggregate a discovery summary over less than 2 DatasetStatistics. Aborted.")
        discovery_summary_schema = {}
        discovery_summary = DiscoverySummary(**discovery_summary_schema)
        return discovery_summary
    else:
        for discovery in response:
            discovery = jsonable_encoder(discovery)
            discovery_item_count += discovery['n_items']
            discovery_feature_count += discovery['n_features']
            for feature in discovery['column_information']:
                if feature['title'] == feature_name:
                    if feature['type'] == 'numeric':
                        data = feature
                        feature_type = 'numeric'

                        discovery_item_count_not_na += data['not_na_elements']
                        discovery_mean += data['mean']
                        discovery_std += data['std']
                        discovery_min += data['min']
                        discovery_max += data['max']
                    else:
                        data = feature
                        feature_type = 'categorical'

                        discovery_item_count_not_na += data['not_na_elements']
                        discovery_number_categories += data['number_categories']
                        discovery_frequency += data['frequency']
                        if data['frequency'] > discovery_frequency:
                            discovery_most_frequent_element = data['most_frequent_element']

            discovery_mean /= len(response)
            discovery_std /= len(response)
            discovery_min /= len(response)
            discovery_max /= len(response)

            discovery_number_categories /= len(response)
            discovery_frequency /= len(response)

            discovery_feature_count /= len(response)

        if feature_type == "categorical":
            discovery_summary_json_categorical = {
                "type": "categorical",
                "title": feature_name,
                "not_na_elements": discovery_item_count_not_na,
                "number_categories": discovery_number_categories,
                "most_frequent_element": discovery_most_frequent_element,
                "frequency": discovery_frequency
            }
        else:
            discovery_summary_json_numeric = {
                "type": "numeric",
                "title": feature_name,
                "not_na_elements": discovery_item_count_not_na,
                "mean": discovery_mean,
                "std": discovery_std,
                "min": discovery_min,
                "max": discovery_max
            }


        if feature_type == 'categorical':
            figure = create_errorbar(discovery_summary_json_categorical)
        else:
            figure = create_errorbar(discovery_summary_json_numeric)

        fig_json = plotly.io.to_json(figure)
        obj = json.loads(fig_json)

        figure_schema = {
            'title': feature_name,
            'type': feature_type,
            'figure': obj
        }

        discovery_figure = DiscoveryFigure(**figure_schema)

        try:
            discovery_summary_json_categorical['figure_data'] = discovery_figure
        except:
            discovery_summary_json_numeric['figure_data'] = discovery_figure

        if feature_type == 'categorical':
            discovery_summary_schema = {
                "proposal_id": proposal_id,
                "item_count": discovery_item_count,
                "feature_count": discovery_feature_count,
                "data_information": [discovery_summary_json_categorical]
            }
        else:
            discovery_summary_schema = {
                "proposal_id": proposal_id,
                "item_count": discovery_item_count,
                "feature_count": discovery_feature_count,
                "data_information": [discovery_summary_json_numeric]
            }

        discovery_summary = DiscoverySummary(**discovery_summary_schema)

        #print("DISCOVERY SUMMARY : {}".format(discovery_summary))

        return discovery_summary

@router.delete("/{proposal_id}/discovery", response_model=DiscoveryStatistics)
def delete_discovery_statistics(proposal_id: int, db: Session = Depends(dependencies.get_db)) -> DiscoveryStatistics:
    discovery_del = datasets.delete_by_dataset_id(proposal_id, db)
    if not discovery_del:
        raise HTTPException(status_code=404, detail=f"DatasetStatistics of proposal with id '{proposal_id}' not found.")
    return discovery_del

@router.post("/{proposal_id}/discovery", response_model=DiscoveryStatistics)
def post_discovery_statistics(proposal_id: int, create_msg: StatisticsCreate, db: Session = Depends(dependencies.get_db)) -> DatasetStatistics:
    dataset = json.loads(create_msg.json())
    discovery_statistics_schema = {
        "proposal_id": proposal_id,
        "n_items": int(dataset['n_items']),
        "n_features": int(dataset['n_features']),
        "column_information": dataset['column_information']
    }
    discovery_statistics = DiscoveryStatistics(**discovery_statistics_schema)
    discovery_statistics = datasets.create(db, obj_in=discovery_statistics)
    if not discovery_statistics:
        raise HTTPException(status_code=404, detail=f"DatasetStatistics of proposal with id '{proposal_id}' could not be created.")
    return discovery_statistics


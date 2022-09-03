from fastapi import APIRouter, Depends, HTTPException
from fastapi.encoders import jsonable_encoder
from typing import Any, List

from pht_federated.aggregator.api.schemas.discovery import SummaryCreate, DiscoverySummary
from pht_federated.aggregator.api.schemas.figures import DiscoveryFigure, DiscoveryFigures
from pht_federated.aggregator.api.crud.crud_discovery import discoveries
from pht_federated.aggregator.api.discoveries.statistics import *

from pht_federated.aggregator.api import dependencies
from sqlalchemy.orm import Session


router = APIRouter()

@router.get("/{proposal_id}/discovery_all", response_model=List[DiscoverySummary])
def get_discovery_all(proposal_id: int, db: Session = Depends(dependencies.get_db)):
    discovery = discoveries.get_all_by_discovery_id(proposal_id, db)
    if not discovery:
        raise HTTPException(status_code=404, detail=f"Discovery of proposal with id '{proposal_id}' not found.")
    return discovery

@router.get("/{proposal_id}/discovery_aggregated_single", response_model=DiscoverySummary)
def get_discovery_single_aggregated(proposal_id: int,  feature_name: str, db: Session = Depends(dependencies.get_db)):

    response = discoveries.get_all_by_discovery_id(proposal_id, db)
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

    for discovery in response:
        discovery = jsonable_encoder(discovery)
        discovery_item_count += discovery['item_count']
        discovery_feature_count += discovery['feature_count']
        for feature in discovery['data_information']:
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

    print("DISCOVERY SUMMARY : {}".format(discovery_summary))

    return discovery_summary

@router.get("/{proposal_id}/discovery_aggregated_all", response_model=DiscoverySummary)
def get_discovery_all_aggregated(proposal_id: int, db: Session = Depends(dependencies.get_db)):

    response = discoveries.get_all_by_discovery_id(proposal_id, db)
    if not response:
        raise HTTPException(status_code=404, detail=f"Discovery of proposal with id '{proposal_id}' not found.")

    feature_lst = []
    aggregated_feature_lst = []
    discovery_item_count = 0
    discovery_feature_count = 0

    for discovery in response:
        discovery = jsonable_encoder(discovery)
        discovery_item_count += discovery['item_count']
        discovery_feature_count += discovery['feature_count']
        for feature in discovery['data_information']:
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

@router.delete("/{proposal_id}/discovery", response_model=DiscoverySummary)
def delete_discovery(proposal_id: int, db: Session = Depends(dependencies.get_db)) -> DiscoverySummary:
    discovery_del = discoveries.delete_by_discovery_id(proposal_id, db)
    if not discovery_del:
        raise HTTPException(status_code=404, detail=f"Discovery of proposal with id '{proposal_id}' not found.")
    return discovery_del

@router.post("/{proposal_id}/discovery", response_model=DiscoverySummary)
def post_discovery(proposal_id: int, create_msg: SummaryCreate, db: Session = Depends(dependencies.get_db)) -> DiscoverySummary:
    discovery = discoveries.create(db, obj_in=create_msg)
    if not discovery:
        raise HTTPException(status_code=404, detail=f"Discovery of proposal with id '{proposal_id}' could not be created.")
    return discovery

@router.get("/{proposal_id}/discovery/plot_single", response_model=DiscoveryFigure)
def get_plot_discovery_aggregated_one_feature(proposal_id: int, feature_name: str, db: Session = Depends(dependencies.get_db)) -> DiscoveryFigures:

    discovery_mean = 0
    discovery_std = 0
    discovery_min = 0
    discovery_max = 0

    discovery_number_categories = 0
    discovery_most_frequent_element = ""
    discovery_frequency = 0

    feature_type = ""

    response = discoveries.get_all_by_discovery_id(proposal_id, db)
    if not response:
        raise HTTPException(status_code=404,
                            detail=f"Discovery of proposal with proposal_id '{proposal_id}'  not found.")

    for discovery in response:
        discovery = jsonable_encoder(discovery)
        for feature in discovery['data_information']:
            if feature['title'] == feature_name:
                if feature['type'] == 'numeric':
                    data = feature
                    feature_type = 'numeric'

                    discovery_mean += data['mean']
                    discovery_std += data['std']
                    discovery_min += data['min']
                    discovery_max += data['max']
                else:
                    data = feature
                    feature_type = 'categorical'

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

        if discovery_most_frequent_element != "":
            discovery_summary_json_categorical = {
                "title": feature_name,
                "number_categories": discovery_number_categories,
                "most_frequent_element": discovery_most_frequent_element,
                "frequency": discovery_frequency
            }
        else:
            discovery_summary_json_numerical = {
                "title": feature_name,
                "mean": discovery_mean,
                "std": discovery_std,
                "min": discovery_min,
                "max": discovery_max
            }

    figure_lst = []


    if feature_type == 'categorical':
        figure = create_errorbar(discovery_summary_json_categorical)
        figure_lst.append({
            'title': feature_name,
            'type': 'categorical'
        })
    else:
        figure = create_errorbar(discovery_summary_json_numerical)
        figure_lst.append({
            'title': feature_name,
            'type': 'numerical'
        })

    fig_json = plotly.io.to_json(figure)
    obj = json.loads(fig_json)
    figure_lst[0]['figure'] = obj


    figure_schema = {
        'fig_data_all': figure_lst
    }

    discovery_figure = DiscoveryFigures(**figure_schema)

    #print("DISCOVERY FIGURE : {}".format(discovery_figure))

    return discovery_figure

@router.get("/{proposal_id}/discovery/plot_all", response_model=DiscoveryFigures)
def get_plot_discovery_aggregated_all_features(proposal_id: int, db: Session = Depends(dependencies.get_db)) -> DiscoveryFigures:

    feature_lst = []
    aggregated_feature_lst = []
    figure_lst = []


    response = discoveries.get_all_by_discovery_id(proposal_id, db)
    if not response:
        raise HTTPException(status_code=404,
                            detail=f"Discovery of proposal with proposal_id '{proposal_id}'  not found.")

    for discovery in response:
        discovery = jsonable_encoder(discovery)
        for feature in discovery['data_information']:
            feature_lst.append(feature)


    for feature in feature_lst:
        if feature['type'] == 'numeric':
            value = feature

            discovery_title = ""
            discovery_mean = 0
            discovery_std = 0
            discovery_min = 0
            discovery_max = 0

            for feature2 in feature_lst:
                if feature2['title'] == value['title']:
                    data = feature2
                    discovery_title = data['title']
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
                "title": discovery_title,
                "type": 'numeric',
                "mean": discovery_mean,
                "std": discovery_std,
                "min": discovery_min,
                "max": discovery_max
            }
            aggregated_feature_lst.append(discovery_summary_json)

            if len(feature_lst) == 0:
                break

        else:
            value = feature

            discovery_title = ""
            discovery_number_categories = 0
            discovery_most_frequent_element = ""
            discovery_frequency = 0

            for feature2 in feature_lst:
                if feature2['title'] == value['title']:
                    data = feature2

                    discovery_title = data['title']
                    discovery_number_categories += data['number_categories']
                    discovery_frequency += data['frequency']
                    if data['frequency'] > discovery_frequency:
                        discovery_most_frequent_element = data['most_frequent_element']

            feature_lst = [x for x in feature_lst if x['title'] != discovery_title]

            discovery_number_categories /= len(response)
            discovery_frequency /= len(response)

            discovery_summary_json = {
                "title": discovery_title,
                "feature_type": 'categorical',
                "number_categories": discovery_number_categories,
                "most_frequent_element": discovery_most_frequent_element,
                "frequency": discovery_frequency
            }
            aggregated_feature_lst.append(discovery_summary_json)

            if len(feature_lst) == 0:
                break

    for i in range(len(aggregated_feature_lst)):
        figure_lst.append({
            'title': aggregated_feature_lst[i]['feature_name'],
            'type': aggregated_feature_lst[i]['feature_type']
        })
        if aggregated_feature_lst[i]['feature_type'] == 'categorical':
            figure = create_errorbar(aggregated_feature_lst[i])
        else:
            figure = create_errorbar(aggregated_feature_lst[i])

        fig_json = plotly.io.to_json(figure)
        obj = json.loads(fig_json)
        figure_lst[i]['figure'] = obj


    figure_schema = {
        'fig_data_all': figure_lst
    }
    discovery_figures = DiscoveryFigures(**figure_schema)

    print("DISCOVERY FIGURES : {}".format(discovery_figures))

    return discovery_figures

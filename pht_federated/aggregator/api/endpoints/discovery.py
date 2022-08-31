from fastapi import APIRouter, Depends, HTTPException
#from pht_federated.aggregator.api.models.discovery import DataSetSummary
from fastapi.encoders import jsonable_encoder
from typing import Any, List

from pht_federated.aggregator.api.schemas.discovery import SummaryCreate
from pht_federated.aggregator.api.schemas.figures import DiscoveryFigure, DiscoveryFigures
from pht_federated.aggregator.api.crud.crud_discovery import discoveries
from pht_federated.aggregator.api.discoveries.statistics import *

from pht_federated.aggregator.api import dependencies
from sqlalchemy.orm import Session



router = APIRouter()


@router.get("/{proposal_id}/discovery", response_model=List[DiscoverySummary])
def get_discovery_all(proposal_id: int, query_all: bool, db: Session = Depends(dependencies.get_db)):
    if query_all:
        discovery = discoveries.get_all_by_discovery_id(proposal_id, db)
    else:
        discovery = list(discoveries.get_by_discovery_id(proposal_id, db))
    if not discovery:
        raise HTTPException(status_code=404, detail=f"Discovery of proposal with id '{proposal_id}' not found.")
    return discovery


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

'''
@router.get("/{proposal_id}/discovery/plot", response_model=DiscoveryFigure)
def get_plot_discovery(proposal_id: int, feature_name: str, db: Session = Depends(dependencies.get_db)):
    discovery = discoveries.get_by_discovery_id(proposal_id, db)
    if not discovery:
        raise HTTPException(status_code=404, detail=f"Discovery of proposal with id '{proposal_id}' not found.")

    data = jsonable_encoder(discovery)

    for feature in data['data_information']:
        if feature['title'] == feature_name:
            data = feature['figure']['fig_data']

    plot_figure(data)
    discovery_figure = DiscoveryFigure(**data)

    return discovery_figure
'''

@router.get("/{proposal_id}/discovery/plot_single", response_model=DiscoveryFigure)
def get_plot_discovery_aggregated_one_feature(proposal_id: int, feature_name: str, db: Session = Depends(dependencies.get_db)):

    discovery_mean = 0
    discovery_std = 0
    discovery_min = 0
    discovery_max = 0

    response = discoveries.get_all_by_discovery_id(proposal_id, db)
    if not response:
        raise HTTPException(status_code=404,
                            detail=f"Discovery of proposal with proposal_id '{proposal_id}'  not found.")

    for discovery in response:
        discovery = jsonable_encoder(discovery)
        for feature in discovery['data_information']:
            if feature['title'] == feature_name:
                data = feature

        discovery_mean += data['mean']
        discovery_std += data['std']
        discovery_min += data['min']
        discovery_max += data['max']



    discovery_mean /= len(response)
    discovery_std /= len(response)
    discovery_min /= len(response)
    discovery_max /= len(response)

    discovery_summary_json = {
        "feature_name": feature_name,
        "discovery_mean": discovery_mean,
        "discovery_std": discovery_std,
        "discovery_min": discovery_min,
        "discovery_max": discovery_max
    }
    figure_lst = []

    figure_lst.append({
        'feature_name': feature_name
    })

    figure = create_errorbar(discovery_summary_json)
    fig_json = plotly.io.to_json(figure)
    obj = json.loads(fig_json)
    figure_lst[0]['figure'] = obj


    figure_schema = {
        'fig_data_all': figure_lst
    }

    print("FIGURE SCHEMA : {}".format(figure_schema))
    discovery_figure = DiscoveryFigures(**figure_schema)

    print("DISCOVERY FIGURE : {}".format(discovery_figure))

    return discovery_figure


@router.get("/{proposal_id}/discovery/plot", response_model=DiscoveryFigures)
def get_plot_discovery_aggregated_all_features(proposal_id: int, db: Session = Depends(dependencies.get_db)):

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
        value = feature

        discovery_title = ""
        discovery_mean = 0
        discovery_std = 0
        discovery_min = 0
        discovery_max = 0

        for feature2 in feature_lst:
            if feature2['title'] == value['title']:
                data = feature2
                #print("DATA : {}".format(data))
                discovery_title = data['title']
                discovery_mean += data['mean']
                discovery_std += data['std']
                discovery_min += data['min']
                discovery_max += data['max']
                #print("DISCOVERY MEAN : {}".format(discovery_mean))

        #print("FEATURE LIST BEFORE : {}".format(feature_lst))
        feature_lst = [x for x in feature_lst if x['title'] != discovery_title]
        #print("FEATURE LIST AFTER : {}".format(feature_lst))



        discovery_mean /= len(response)
        discovery_std /= len(response)
        discovery_min /= len(response)
        discovery_max /= len(response)

        discovery_summary_json = {
            "feature_name": discovery_title,
            "discovery_mean": discovery_mean,
            "discovery_std": discovery_std,
            "discovery_min": discovery_min,
            "discovery_max": discovery_max
        }
        aggregated_feature_lst.append(discovery_summary_json)

        if len(feature_lst) == 0:
            break

    print("AGGREGATED FEATURE LST : {}".format(aggregated_feature_lst))


    for i in range(len(aggregated_feature_lst)):
        figure_lst.append({
            'feature_name': aggregated_feature_lst[i]['feature_name']
        })

        figure = create_errorbar(aggregated_feature_lst[i])
        fig_json = plotly.io.to_json(figure)
        obj = json.loads(fig_json)
        figure_lst[i]['figure'] = obj


    figure_schema = {
        'fig_data_all': figure_lst
    }

    print("FIGURE SCHEMA : {}".format(figure_schema))

    discovery_figures = DiscoveryFigures(**figure_schema)

    print("DISCOVERY FIGURES : {}".format(discovery_figures))

    return discovery_figures




from fastapi import APIRouter, Depends, HTTPException
#from pht_federated.aggregator.api.models.discovery import DataSetSummary
from fastapi.encoders import jsonable_encoder

from pht_federated.aggregator.api.schemas.discovery import SummaryCreate
from pht_federated.aggregator.api.crud.crud_discovery import discoveries
from pht_federated.aggregator.api.discoveries.statistics import *

from pht_federated.aggregator.api import dependencies
from sqlalchemy.orm import Session



router = APIRouter()


@router.get("/{proposal_id}/discovery", response_model=DiscoverySummary)
def get_proposal(proposal_id: int, db: Session = Depends(dependencies.get_db)) -> DiscoverySummary:
    discovery = discoveries.get_by_discovery_id(proposal_id, db)
    if not discovery:
        raise HTTPException(status_code=404, detail=f"Discovery of proposal with id '{proposal_id}' not found.")
    return discovery


@router.delete("/{proposal_id}/discovery", response_model=DiscoverySummary)
def delete_proposal(proposal_id: int, db: Session = Depends(dependencies.get_db)) -> DiscoverySummary:
    discovery_del = discoveries.delete_by_discovery_id(proposal_id, db)
    if not discovery_del:
        raise HTTPException(status_code=404, detail=f"Discovery of proposal with id '{proposal_id}' not found.")
    return discovery_del



@router.post("/{proposal_id}/discovery", response_model=DiscoverySummary)
def post_proposal(proposal_id: int, create_msg: SummaryCreate, db: Session = Depends(dependencies.get_db)) -> DiscoverySummary:
    discovery = discoveries.create(db, obj_in=create_msg)
    if not discovery:
        raise HTTPException(status_code=404, detail=f"Discovery of proposal with id '{proposal_id}' could not be created.")
    return discovery


@router.get("/{proposal_id}/discovery/plot", response_model=DiscoveryFigure)
def get_plot_proposal(proposal_id: int, feature_name: str, db: Session = Depends(dependencies.get_db)):
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





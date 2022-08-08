from fastapi import APIRouter, Depends, HTTPException
#from pht_federated.aggregator.api.models.discovery import DataSetSummary
from pht_federated.aggregator.api.schemas.discovery import DataSetSummary, SummaryCreate, DataSetStatistics, DataSetFigure
from pht_federated.aggregator.api.discoveries import statistics
from pht_federated.aggregator.api.crud.crud_discovery import discoveries
from pht_federated.aggregator.api.endpoints import dependencies
from sqlalchemy.orm import Session
import pandas as pd
import plotly, json



router = APIRouter()


@router.get("/{proposal_id}/discovery", response_model=DataSetSummary)
def get_proposal(proposal_id: int, db: Session = Depends(dependencies.get_db)) -> DataSetSummary:
    discovery = discoveries.get(db, proposal_id)
    if not discovery:
        raise HTTPException(status_code=404, detail=f"Discovery of proposal with id '{proposal_id}' not found.")
    return discovery


@router.delete("/{proposal_id}/discovery", response_model=DataSetSummary)
def delete_proposal(proposal_id: int, db: Session = Depends(dependencies.get_db)) -> DataSetSummary:
    discovery = discoveries.get(db, proposal_id)
    if not discovery:
        raise HTTPException(status_code=404, detail=f"Discovery of proposal with id '{proposal_id}' not found.")
    discovery_del = discoveries.remove(db=db, id=proposal_id)
    return discovery_del



@router.post("/{proposal_id}/discovery", response_model=DataSetSummary)
def post_proposal(proposal_id: int, create_msg: SummaryCreate, db: Session = Depends(dependencies.get_db)) -> DataSetSummary:
    discovery = discoveries.create(db, obj_in=create_msg)
    if not discovery:
        raise HTTPException(status_code=404, detail=f"Discovery of proposal with id '{proposal_id}' could not be created.")
    return discovery


@router.post("/{proposal_id}/discovery/plot_{feature_name}", response_model=DataSetFigure)
def post_plot_proposal(proposal_id: int, feature_name: str, db: Session = Depends(dependencies.get_db)):
    discovery = discoveries.get(db, proposal_id)
    if not discovery:
        raise HTTPException(status_code=404, detail=f"Discovery of proposal with id '{proposal_id}' not found.")

    data = discovery.json()
    for feature in data['data_information']:
        if feature['title'] == feature_name:
            data = feature['figure']['fig_data']
    obj = json.loads(data)
    figure = DataSetFigure(fig_data=obj)

    print("FIGURE : {}".format(figure))

    discoveries.create_plot(figure)





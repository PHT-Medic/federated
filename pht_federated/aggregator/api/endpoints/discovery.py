from fastapi import APIRouter, Depends, HTTPException
#from pht_federated.aggregator.api.models.discovery import DataSetSummary
from pht_federated.aggregator.api.schemas.discovery import DataSetSummary, SummaryCreate, DataSetStatistics
from pht_federated.aggregator.api.discoveries import statistics
from pht_federated.aggregator.api.crud.crud_discovery import discoveries
from pht_federated.aggregator.api.endpoints import dependencies
from sqlalchemy.orm import Session
import pandas as pd



router = APIRouter()


@router.get("/{proposal_id}/discovery", response_model=DataSetSummary)
def get_proposal(proposal_id: int, db: Session = Depends(dependencies.get_db)) -> DataSetSummary:
    discovery = discoveries.get_by_discovery_id(proposal_id, db)
    if not discovery:
        raise HTTPException(status_code=404, detail=f"Discovery with id '{proposal_id}' not found.")
    return discovery


@router.delete("/{proposal_id}/discovery", response_model=DataSetSummary)
def delete_proposal(proposal_id: int, db: Session = Depends(dependencies.get_db)) -> DataSetSummary:
    discovery = discoveries.get_by_discovery_id(proposal_id, db)
    if not discovery:
        raise HTTPException(status_code=404, detail=f"Discovery with id '{proposal_id}' not found.")
    discovery_del = discoveries.remove(db=db, id=proposal_id)
    return discovery_del



@router.post("/{proposal_id}/discovery", response_model=DataSetSummary)
def post_proposal(proposal_id: int, create_msg: SummaryCreate, db: Session = Depends(dependencies.get_db)) -> DataSetSummary:
    discovery = discoveries.create(db, obj_in=create_msg)
    if not discovery:
        raise HTTPException(status_code=404, detail=f"Discovery with id '{proposal_id}' could not be created.")
    return discovery


@router.get("/{proposal_id}/discovery/figures", response_model=DataSetSummary)
def plot_proposal(proposal_id: int, db: Session = Depends(dependencies.get_db)):
    discovery = discoveries.get_by_discovery_id(proposal_id, db)
    if not discovery:
        raise HTTPException(status_code=404, detail=f"Discovery with id '{proposal_id}' not found.")
    discovery_stats = get_data_set_statistics(discovery)



@router.get("/{proposal_id}/discovery", response_model=DataSetSummary)
def get_data_set_statistics(discovery: DataSetSummary):
    try:
        discovery_df = pd.read_csv(discovery)
    except NotImplementedError:
        raise HTTPException(status_code=422, detail="Method just specified for CSV-Data.")
    if discovery_df is None or discovery_df.empty:
        raise HTTPException(status_code=404, detail="Discovery not found.")
    try:
        stats = statistics.get_dataset_statistics(discovery_df)
        print("Returned Discovery (DataSet) statistics : {}".format(stats))
        return stats
    except TypeError:
        raise HTTPException(status_code=400, detail="Discovery has to be given as a dataframe.")

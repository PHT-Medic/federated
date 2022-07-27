from fastapi import APIRouter, Depends, HTTPException
from pht_federated.aggregator.api.models.discovery import DataSetSummary
from pht_federated.aggregator.api.schemas.discovery import DataSetSummary
from pht_federated.aggregator.api.crud.crud_discovery import discoveries


router = APIRouter()


@router.get("/{proposal_id}/discovery", response_model=DataSetSummary)
def get_proposal(proposal_id: int, db: Session) -> DataSetSummary:
    discovery = discoveries.get_by_discovery_id(proposal_id, db)
    if not discovery:
        raise HTTPException(status_code=404, detail=f"Discovery with id '{proposal_id}' not found.")
    return discovery



@router.post("/{proposal_id}/discovery", response_model=DataSetSummary)
def post_proposal(proposal_id: int, db: Session) -> DataSetSummary:
    discovery = discoveries.get_by_discovery_id(proposal_id, db)
    if not discovery:
        raise HTTPException(status_code=404, detail=f"Discovery with id '{proposal_id}' not found.")
    return discovery


@router.get("/{proposal_id}/discovery/figures", response_model=DataSetSummary)
def plot_proposal(proposal_id: int, db: Session):
    return None

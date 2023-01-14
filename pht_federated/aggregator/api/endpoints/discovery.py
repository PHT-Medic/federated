from typing import List, Union

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from pht_federated.aggregator.api import dependencies
from pht_federated.aggregator.crud.crud_dataset_statistics import dataset_statistics
from pht_federated.aggregator.crud.crud_discovery import discoveries
from pht_federated.aggregator.crud.crud_proposals import proposals
from pht_federated.aggregator.schemas.dataset_statistics import (
    DatasetStatistics,
    DiscoveryStatistics,
    StatisticsCreate,
)
from pht_federated.aggregator.schemas.discovery import (
    DataDiscovery,
    DataDiscoveryCreate,
    DataDiscoveryUpdate,
    DiscoverySummary,
)
from pht_federated.aggregator.services.discovery.utility_functions import (
    aggregate_proposal_features,
)

router = APIRouter()


@router.post("/{proposal_id}/discoveries", response_model=DataDiscovery)
def create_discovery(
    proposal_id: str,
    discovery_create: DataDiscoveryCreate,
    db: Session = Depends(dependencies.get_db),
) -> DataDiscovery:
    # Check if proposal exists
    if not proposals.get(db=db, id=proposal_id):
        raise HTTPException(
            status_code=400, detail=f"Proposal with id {proposal_id} does not exist"
        )

    discovery_create.proposal_id = proposal_id
    discovery = discoveries.create(db, obj_in=discovery_create)
    return discovery


@router.get("/{proposal_id}/discoveries", response_model=List[DataDiscovery])
def get_all_discoveries(
    proposal_id: str,
    db: Session = Depends(dependencies.get_db),
    skip: int = 0,
    limit: int = 100,
) -> List[DataDiscovery]:
    # Check if proposal exists
    db_proposal = proposals.get(db=db, id=proposal_id)
    if not db_proposal:
        raise HTTPException(
            status_code=404, detail=f"Proposal with id {proposal_id} does not exist"
        )

    return db_proposal.discoveries[skip : skip + limit]


@router.get("/{proposal_id}/discoveries/{discovery_id}", response_model=DataDiscovery)
def get_discovery(
    proposal_id: str, discovery_id: str, db: Session = Depends(dependencies.get_db)
) -> DataDiscovery:
    # Check if proposal exists
    if not proposals.get(db=db, id=proposal_id):
        raise HTTPException(
            status_code=404, detail=f"Proposal with id {proposal_id} does not exist"
        )

    discovery = discoveries.get(db, discovery_id)
    if not discovery:
        raise HTTPException(
            status_code=404, detail=f"Discovery - {discovery_id} - not found"
        )
    return discovery


@router.put("/{proposal_id}/discoveries/{discovery_id}", response_model=DataDiscovery)
def update_discovery(
    proposal_id: str,
    discovery_id: str,
    discovery_update: DataDiscoveryUpdate,
    db: Session = Depends(dependencies.get_db),
) -> DataDiscovery:
    # Check if proposal exists
    if not proposals.get(db=db, id=proposal_id):
        raise HTTPException(
            status_code=404, detail=f"Proposal with id {proposal_id} does not exist"
        )

    discovery = discoveries.get(db, discovery_id)
    if not discovery:
        raise HTTPException(
            status_code=404, detail=f"Discovery - {discovery_id} - not found"
        )

    updated = discoveries.update(db, db_obj=discovery, obj_in=discovery_update)
    return updated


@router.delete(
    "/{proposal_id}/discoveries/{discovery_id}", response_model=DataDiscovery
)
def delete_discovery(
    proposal_id: str, discovery_id: str, db: Session = Depends(dependencies.get_db)
) -> DataDiscovery:
    # Check if proposal exists
    if not proposals.get(db=db, id=proposal_id):
        raise HTTPException(
            status_code=404, detail=f"Proposal with id {proposal_id} does not exist"
        )

    discovery = discoveries.get(db, discovery_id)
    if not discovery:
        raise HTTPException(
            status_code=404, detail=f"Discovery - {discovery_id} - not found"
        )
    discovery = discoveries.remove(db, id=discovery_id)
    return discovery


@router.get(
    "/{proposal_id}/discoveries/{discovery_id}/summary", response_model=DiscoverySummary
)
def get_discovery_summary(
    proposal_id: str,
    discovery_id: int,
    features: Union[str, None] = Query(default=None),
    db: Session = Depends(dependencies.get_db),
):
    try:
        response = dataset_statistics.get_all_by_discovery_id(discovery_id, db)
    except ValueError:
        raise HTTPException(
            status_code=403,
            detail="Not able to aggregate a discovery summary over less than 2 DatasetStatistics. Aborted.",
        )
    if not response:
        raise HTTPException(
            status_code=404,
            detail=f"Discovery of proposal with id '{proposal_id}' not found.",
        )

    discovery_summary = aggregate_proposal_features(response, proposal_id, features)
    discovery_summary.discovery_id = discovery_id
    #print("DISCOVERY SUMMARY : {}".format(discovery_summary.json()))

    return discovery_summary


@router.post(
    "/{proposal_id}/discoveries/{discovery_id}/stats",
    response_model=DiscoveryStatistics,
)
def post_discovery_statistics(
    proposal_id: str,
    discovery_id: int,
    create_msg: StatisticsCreate,
    db: Session = Depends(dependencies.get_db),
) -> DatasetStatistics:
    proposal = proposals.get(db, proposal_id)
    if not proposal:
        raise HTTPException(
            status_code=404, detail=f"Proposal with id '{proposal_id}' not found."
        )

    discovery = discoveries.get(db, discovery_id)
    if not discovery:
        raise HTTPException(
            status_code=404, detail=f"Discovery with id '{discovery_id}' not found."
        )

    # todo add user/robot id
    create_dict = {
        **create_msg.dict(),
        "discovery_id": discovery_id,
    }
    db_create_message = StatisticsCreate(**create_dict)
    discovery_statistics = dataset_statistics.create(db, obj_in=db_create_message)
    if not discovery_statistics:
        raise HTTPException(
            status_code=400,
            detail=f"DatasetStatistics of proposal with id '{proposal_id}' could not be created.",
        )
    return discovery_statistics

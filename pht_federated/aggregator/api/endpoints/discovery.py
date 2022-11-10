from fastapi import APIRouter, Depends, HTTPException, Query
from pht_federated.aggregator.api.schemas.dataset_statistics import *
from pht_federated.aggregator.api.schemas.proposals import *
from pht_federated.aggregator.api.crud.crud_dataset_statistics import datasets
from pht_federated.aggregator.api.crud.crud_proposals import proposals
from pht_federated.aggregator.api.discoveries.utility_functions import *
from pht_federated.aggregator.api import dependencies
from sqlalchemy.orm import Session
from datetime import datetime

router = APIRouter()


@router.get("/{proposal_id}/discovery", response_model=DiscoverySummary)
def get_discovery_all(proposal_id: str, query: Union[str, None] = Query(default=None),
                      db: Session = Depends(dependencies.get_db)):
    try:
        response = datasets.get_all_by_proposal_id(proposal_id, db)
    except ValueError:
        raise HTTPException(status_code=403, detail="Not able to aggregate a discovery summary over less than 2 DatasetStatistics. Aborted.")
    if not response:
        raise HTTPException(status_code=404, detail=f"Discovery of proposal with id '{proposal_id}' not found.")


    discovery_summary = aggregate_proposal_features(response, proposal_id, query)

    # print("DISCOVERY SUMMARY : {}".format(discovery_summary))

    return discovery_summary


@router.delete("/{proposal_id}/discovery", response_model=int)
def delete_discovery_statistics(proposal_id: str, db: Session = Depends(dependencies.get_db)) -> int:
    discovery_del = datasets.delete_by_proposal_id(proposal_id, db)
    if not discovery_del:
        raise HTTPException(status_code=404, detail=f"DatasetStatistics of proposal with id '{proposal_id}' not found.")
    return discovery_del


@router.post("/{proposal_id}/discovery", response_model=DiscoveryStatistics)
def post_discovery_statistics(proposal_id: str, create_msg: StatisticsCreate,
                              db: Session = Depends(dependencies.get_db)) -> DatasetStatistics:

    dataset_statistics = create_msg.dict()
    discovery_statistics_schema = {
        "id": uuid.uuid4(),
        "proposal_id": proposal_id,
        "item_count": dataset_statistics['item_count'],
        "feature_count": dataset_statistics['feature_count'],
        "column_information": dataset_statistics['column_information']
    }
    discovery_statistics = StatisticsCreate(**discovery_statistics_schema)
    discovery_statistics = datasets.create(db, obj_in=discovery_statistics)
    if not discovery_statistics:
        raise HTTPException(status_code=400,
                            detail=f"DatasetStatistics of proposal with id '{proposal_id}' could not be created.")
    return discovery_statistics


@router.post("/{proposal_id}", response_model=Proposals)
def post_proposal(proposal_id: str, db: Session = Depends(dependencies.get_db)) -> Proposals:

    proposal_schema = {
        "id": proposal_id,
        "name": "example_proposal-" + str(uuid.uuid4()),
        "created_at": datetime.now(),
        "updated_at": datetime.now()
    }
    proposal = ProposalsCreate(**proposal_schema)
    proposal = proposals.create(db, obj_in=proposal)
    if not proposal:
        raise HTTPException(status_code=400,
                            detail=f"DatasetStatistics of proposal with id '{proposal_id}' could not be created.")

    return proposal

@router.delete("/{proposal_id}", response_model=int)
def delete_proposal(proposal_id: str, db: Session = Depends(dependencies.get_db)) -> int:
    proposal_del = proposals.delete_by_proposal_id(proposal_id, db)
    if not proposal_del:
        raise HTTPException(status_code=404, detail=f"Proposal with id '{proposal_id}' not found.")
    return proposal_del
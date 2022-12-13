from fastapi import APIRouter, Depends, HTTPException, Query
from pht_federated.aggregator.schemas.dataset_statistics import *
from pht_federated.aggregator.schemas.discovery import DiscoverySummary
from pht_federated.aggregator.crud.crud_dataset_statistics import dataset_statistics
from pht_federated.aggregator.crud.crud_proposals import proposals
from pht_federated.aggregator.api.discoveries.utility_functions import *
from pht_federated.aggregator.api import dependencies
from sqlalchemy.orm import Session

router = APIRouter()


@router.get("/{proposal_id}/discovery", response_model=DiscoverySummary)
def get_discovery_all(proposal_id: str, features: Union[str, None] = Query(default=None),
                      db: Session = Depends(dependencies.get_db)):
    try:
        response = dataset_statistics.get_all_by_proposal_id(proposal_id, db)
    except ValueError:
        raise HTTPException(status_code=403, detail="Not able to aggregate a discovery summary over less than 2 DatasetStatistics. Aborted.")
    if not response:
        raise HTTPException(status_code=404, detail=f"Discovery of proposal with id '{proposal_id}' not found.")


    discovery_summary = aggregate_proposal_features(response, proposal_id, features)

    # print("DISCOVERY SUMMARY : {}".format(discovery_summary))

    return discovery_summary


@router.delete("/{proposal_id}/discovery", response_model=int)
def delete_discovery_statistics(proposal_id: str, db: Session = Depends(dependencies.get_db)) -> int:
    discovery_del = dataset_statistics.delete_by_proposal_id(proposal_id, db)
    if not discovery_del:
        raise HTTPException(status_code=404, detail=f"DatasetStatistics of proposal with id '{proposal_id}' not found.")
    return discovery_del


@router.post("/{proposal_id}/discovery/{discovery_id}", response_model=DiscoveryStatistics)
def post_discovery_statistics(proposal_id: str, create_msg: StatisticsCreate,
                              db: Session = Depends(dependencies.get_db)) -> DatasetStatistics:


    proposal = proposals.get(db, proposal_id)
    if not proposal:
        raise HTTPException(status_code=404, detail=f"Proposal with id '{proposal_id}' not found.")



    stats = create_msg.dict()
    discovery_statistics_schema = {
        "id": uuid.uuid4(),
        "proposal_id": proposal_id,
        **stats
    }
    discovery_statistics = StatisticsCreate(**discovery_statistics_schema)
    discovery_statistics = dataset_statistics.create(db, obj_in=discovery_statistics)
    if not discovery_statistics:
        raise HTTPException(status_code=400,
                            detail=f"DatasetStatistics of proposal with id '{proposal_id}' could not be created.")
    return discovery_statistics
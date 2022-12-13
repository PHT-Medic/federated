from sqlalchemy.orm import Session
from fastapi import Depends
from .base import CRUDBase
from typing import List
from pht_federated.aggregator.models.discovery import DiscoverySummary, DataDiscovery
from pht_federated.aggregator.schemas.discovery import SummaryCreate, SummaryUpdate, DataDiscoveryCreate, DataDiscoveryUpdate


class CRUDDiscovery(CRUDBase[DataDiscovery, DataDiscoveryCreate, DataDiscoveryUpdate]):
    pass



class CRUDDiscoverySummary(CRUDBase[DiscoverySummary, SummaryCreate, SummaryUpdate]):

    def get_by_proposal_id(self, proposal_id: int, db: Session) -> List[
        DiscoverySummary]:
        discovery = db.query(DiscoverySummary).filter(DiscoverySummary.proposal_id == proposal_id).first()
        return discovery

    def delete_by_proposal_id(self, proposal_id: int, db: Session) -> DiscoverySummary:
        discovery_del = db.query(DiscoverySummary).filter(DiscoverySummary.proposal_id == proposal_id).delete()
        return discovery_del


discovery_summaries = CRUDDiscoverySummary(DiscoverySummary)

discoveries = CRUDDiscovery(DataDiscovery)

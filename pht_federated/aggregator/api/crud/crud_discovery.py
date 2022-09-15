from sqlalchemy.orm import Session
from fastapi import Depends
from typing import Any, List
from .base import CRUDBase, CreateSchemaType, ModelType, Optional
from pht_federated.aggregator.api.models.discovery import DiscoverySummary
from pht_federated.aggregator.api.schemas.discovery import SummaryCreate, SummaryUpdate
from .. import dependencies


class CRUDDiscoveries(CRUDBase[DiscoverySummary, SummaryCreate, SummaryUpdate]):

    def get_by_proposal_id(self, proposal_id: int, db: Session = Depends(dependencies.get_db)) -> DiscoverySummary:
        discovery = db.query(DiscoverySummary).filter(DiscoverySummary.proposal_id == proposal_id).first()
        return discovery

    def get_all_by_proposal_id(self, proposal_id: int, db: Session = Depends(dependencies.get_db)) -> List[DiscoverySummary]:
        discovery = db.query(DiscoverySummary).filter(DiscoverySummary.proposal_id == proposal_id).all()
        return discovery

    def delete_by_proposal_id(self, proposal_id: int, db: Session = Depends(dependencies.get_db)) -> DiscoverySummary:
        discovery_del = db.query(DiscoverySummary).filter(DiscoverySummary.proposal_id == proposal_id).delete()
        return discovery_del


discoveries = CRUDDiscoveries(DiscoverySummary)

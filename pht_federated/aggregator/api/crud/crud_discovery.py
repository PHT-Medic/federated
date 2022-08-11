from sqlalchemy.orm import Session
from fastapi import Depends
from .base import CRUDBase, CreateSchemaType, ModelType, Optional
from fastapi.encoders import jsonable_encoder
from pht_federated.aggregator.api.models.discovery import DiscoverySummary
from pht_federated.aggregator.api.schemas.discovery import SummaryCreate, SummaryUpdate
from .. import dependencies


class CRUDDiscoveries(CRUDBase[DiscoverySummary, SummaryCreate, SummaryUpdate]):

    def get_by_discovery_id(self, proposal_id: int, db: Session = Depends(dependencies.get_db)) -> DiscoverySummary:
        discovery = db.query(DiscoverySummary).filter(DiscoverySummary.proposal_id == proposal_id).first()
        return discovery

    def get_all_by_discovery_id(self, proposal_id: int, db: Session = Depends(dependencies.get_db)) -> list[DiscoverySummary]:
        discovery = db.query(DiscoverySummary).filter(DiscoverySummary.proposal_id == proposal_id).all()
        return discovery

    def get_by_discovery_id_and_station_id(self, proposal_id: int, station_id: int, db: Session = Depends(dependencies.get_db)) -> DiscoverySummary:
        discovery = db.query(DiscoverySummary).filter(DiscoverySummary.proposal_id == proposal_id,
                                                      DiscoverySummary.station_id == station_id).first()
        return discovery

    def delete_by_discovery_id(self, proposal_id: int, db: Session = Depends(dependencies.get_db)) -> DiscoverySummary:
        discovery_del = db.query(DiscoverySummary).filter(DiscoverySummary.proposal_id == proposal_id).delete()
        return discovery_del


discoveries = CRUDDiscoveries(DiscoverySummary)

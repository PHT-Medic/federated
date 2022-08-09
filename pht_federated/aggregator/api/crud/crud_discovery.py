from sqlalchemy.orm import Session
from fastapi import APIRouter, Depends, HTTPException
from .base import CRUDBase, CreateSchemaType, ModelType, Optional
from fastapi.encoders import jsonable_encoder
from pht_federated.aggregator.api.models.discovery import DiscoverySummary
from pht_federated.aggregator.api.schemas.discovery import SummaryCreate, SummaryUpdate, FigureData, DiscoveryFigure
from pht_federated.aggregator.api.endpoints import dependencies
import plotly, json


class CRUDDiscoveries(CRUDBase[DiscoverySummary, SummaryCreate, SummaryUpdate]):

    def create(self, db: Session = Depends(dependencies.get_db), *, obj_in: CreateSchemaType) -> Optional[ModelType]:
        obj_in_data = jsonable_encoder(obj_in)
        db_obj = self.model(**obj_in_data)
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)

        return db_obj

    def get_by_discovery_id(self, proposal_id: int, db: Session = Depends(dependencies.get_db)) -> DiscoverySummary:
        discovery = db.query(DiscoverySummary).filter(DiscoverySummary.proposal_id == proposal_id).first()
        return discovery

    def delete_by_discovery_id(self, proposal_id: int, db: Session = Depends(dependencies.get_db)) -> DiscoverySummary:
        discovery_del = db.query(DiscoverySummary).filter(DiscoverySummary.proposal_id == proposal_id).delete()
        return discovery_del


discoveries = CRUDDiscoveries(DiscoverySummary)

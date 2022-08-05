from sqlalchemy.orm import Session
from fastapi import APIRouter, Depends, HTTPException
from .base import CRUDBase, CreateSchemaType, ModelType, Optional
from fastapi.encoders import jsonable_encoder
from pht_federated.aggregator.api.models.discovery import DataSetSummary
from pht_federated.aggregator.api.schemas.discovery import SummaryCreate, SummaryUpdate
from pht_federated.aggregator.api.endpoints import dependencies


class CRUDDiscoveries(CRUDBase[DataSetSummary, SummaryCreate, SummaryUpdate]):

    def create(self, db: Session = Depends(dependencies.get_db), *, obj_in: CreateSchemaType) -> Optional[ModelType]:
        obj_in_data = jsonable_encoder(obj_in)
        db_obj = self.model(**obj_in_data)
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)

        return db_obj

    def get_by_discovery_id(self, proposal_id: int, db: Session = Depends(dependencies.get_db)) -> DataSetSummary:
        discovery = db.query(DataSetSummary).filter(DataSetSummary.proposal_id == proposal_id).first()
        return discovery






discoveries = CRUDDiscoveries(DataSetSummary)

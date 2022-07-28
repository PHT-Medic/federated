from sqlalchemy.orm import Session

from .base import CRUDBase, CreateSchemaType, ModelType, Optional
from fastapi.encoders import jsonable_encoder
from pht_federated.aggregator.api.models.discovery import DataSetSummary
from pht_federated.aggregator.api.schemas.discovery import SummaryCreate, SummaryUpdate


class CRUDDiscoveries(CRUDBase[DataSetSummary, SummaryCreate, SummaryUpdate]):

    def create(self, db: Session, *, obj_in: CreateSchemaType) -> Optional[ModelType]:
        obj_in_data = jsonable_encoder(obj_in)
        db_obj = self.model(**obj_in_data)
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)

        return db_obj

    def get_by_discovery_id(self, db: Session, proposal_id: int) -> DataSetSummary:
        discovery = db.query(DataSetSummary).filter(DataSetSummary.proposal_id == proposal_id).first()
        return discovery




discoveries = CRUDDiscoveries(DataSetSummary)

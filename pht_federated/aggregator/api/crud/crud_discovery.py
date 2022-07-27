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

    def add_if_not_exists(self, db: Session, train_id: str, created_at: str = datetime.now(), updated_at: str = None):
        db_train = self.get_by_train_id(db, train_id)
        if not db_train:
            if updated_at:
                db_train = DockerTrain(train_id=train_id, created_at=parser.parse(created_at),
                                       updated_at=parser.parse(updated_at))
            else:
                db_train = DockerTrain(train_id=train_id, created_at=parser.parse(created_at))
            db.add(db_train)
            db.commit()
            db.refresh(db_train)
            train_state = DockerTrainState(train_id=db_train.id)
            db.add(train_state)
            db.commit()
            return db_train


discoveries = CRUDDiscoveries(DataSetSummary)

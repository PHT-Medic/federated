from sqlalchemy.orm import Session

from .base import CRUDBase, CreateSchemaType, ModelType, Optional
from fastapi.encoders import jsonable_encoder
from pht_federated.aggregator.api.models.discovery import DataSetSummary
from pht_federated.aggregator.api.schemas.discovery import SummaryCreate, SummaryUpdate
from .base import CRUDBase


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

    def get_data(self, db: Session, proposal_id: int):
        dataset = self.get_by_discovery_id(db, proposal_id)
        if dataset.data_type == "image":
            raise NotImplementedError
        elif dataset.data_type == "csv":
            path = dataset.access_path
            file = get_file(path, dataset.storage_type)
            with file as f:
                csv_df = pd.read_csv(f)
                return csv_df
        elif dataset.data_type == "directory":
            raise NotImplementedError
        elif dataset.data_type == "fhir":
            raise NotImplementedError
        return dataset

    def add_stats(self, db:Session, proposal_id, stats):
        dataset = self.get(db, proposal_id)
        stats = jsonable_encoder(stats)
        stats_json = json.dumps(stats)
        dataset.summary = stats_json
        db.commit()
        db.refresh(dataset)
        return dataset



discoveries = CRUDDiscoveries(DataSetSummary)

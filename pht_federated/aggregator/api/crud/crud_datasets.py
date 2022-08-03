from sqlalchemy.orm import Session
import pandas as pd
import json

from .base import CRUDBase, CreateSchemaType, ModelType, Optional, Any
from fastapi.encoders import jsonable_encoder
from pht_federated.aggregator.api.models.discovery import DataSet
from pht_federated.aggregator.api.schemas import *
#from station.app.datasets.filesystem import get_file


class CRUDDatasets(CRUDBase[DataSet, DataSetCreate, DataSetUpdate]):

    # TODO fix MinIO Client connection
    # using the .create function from the base CRUD operators
    def create(self, db: Session, *, obj_in: CreateSchemaType) -> ModelType:
        obj_in_data = jsonable_encoder(obj_in)
        db_obj = self.model(**obj_in_data)
        # TODO check for multiple files
        # try:
        #     file = get_file(db_obj.access_path, db_obj.storage_type)

        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)

        return db_obj

    def get_data(self, db: Session, data_set_id):
        dataset = self.get(db, data_set_id)
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

    def get_by_name(self, db: Session, name: str):
        dataset = db.query(self.model).filter(self.model.name == name).first()
        return dataset

    def add_stats(self, db:Session, data_set_id, stats):
        dataset = self.get(db, data_set_id)
        stats = jsonable_encoder(stats)
        stats_json = json.dumps(stats)
        dataset.summary = stats_json
        db.commit()
        db.refresh(dataset)
        return dataset


datasets = CRUDDatasets(DataSet)

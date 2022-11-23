from sqlalchemy.orm import Session
from fastapi import Depends
from typing import Any, List
from .base import CRUDBase, CreateSchemaType, ModelType, Optional
from pht_federated.aggregator.api.models.dataset_statistics import DatasetStatistics
from pht_federated.aggregator.api.schemas.dataset_statistics import StatisticsCreate, StatisticsUpdate
from .. import dependencies


class CRUDDatasetStatistics(CRUDBase[DatasetStatistics, StatisticsCreate, StatisticsUpdate]):


    def get_all_by_proposal_id(self, proposal_id: int, db: Session = Depends(dependencies.get_db)) -> List[DatasetStatistics]:
        dataset = db.query(DatasetStatistics).filter(DatasetStatistics.proposal_id == proposal_id).all()
        return dataset

    def delete_by_proposal_id(self, proposal_id: int, db: Session = Depends(dependencies.get_db)) -> int:
        dataset_del = db.query(DatasetStatistics).filter(DatasetStatistics.proposal_id == proposal_id).delete()
        return dataset_del


datasets = CRUDDatasetStatistics(DatasetStatistics)

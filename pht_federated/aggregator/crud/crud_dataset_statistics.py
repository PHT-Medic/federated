from typing import List

from sqlalchemy.orm import Session

from pht_federated.aggregator.models.dataset_statistics import DatasetStatistics
from pht_federated.aggregator.schemas.dataset_statistics import (
    StatisticsCreate,
    StatisticsUpdate,
)

from .base import CRUDBase


class CRUDDatasetStatistics(
    CRUDBase[DatasetStatistics, StatisticsCreate, StatisticsUpdate]
):
    def get_all_by_discovery_id(
        self, discovery_id: int, db: Session
    ) -> List[DatasetStatistics]:
        dataset = (
            db.query(DatasetStatistics)
            .filter(DatasetStatistics.discovery_id == discovery_id)
            .all()
        )
        return dataset

    def delete_by_proposal_id(self, proposal_id: int, db: Session) -> int:
        dataset_del = (
            db.query(DatasetStatistics)
            .filter(DatasetStatistics.proposal_id == proposal_id)
            .delete()
        )
        return dataset_del


dataset_statistics = CRUDDatasetStatistics(DatasetStatistics)

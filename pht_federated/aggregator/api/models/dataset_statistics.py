from pht_federated.aggregator.db.base_class import Base
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, JSON
from sqlalchemy.dialects.postgresql import UUID
from datetime import datetime
import uuid


class DatasetStatistics(Base):
    __tablename__ = "dataset_statistics"
    id = Column(UUID(as_uuid=True), primary_key=True, index=True, default=uuid.uuid4)
    item_count = Column(Integer, default=0)
    feature_count = Column(Integer, default=0)
    column_information = Column(JSON, default={})

from datetime import datetime
import uuid

from sqlalchemy.orm import relationship
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, JSON
from sqlalchemy.dialects.postgresql import UUID

from pht_federated.aggregator.db.base_class import Base




class DatasetStatistics(Base):
    __tablename__ = "dataset_statistics"
    id = Column(UUID(as_uuid=True), primary_key=True, index=True, default=uuid.uuid4)
    discovery_id = Column(Integer, ForeignKey('data_discovery.id', ondelete="CASCADE"))
    discovery = relationship("DataDiscovery", back_populates="dataset_statistics")
    item_count = Column(Integer, default=0)
    feature_count = Column(Integer, default=0)
    column_information = Column(JSON, default={})
    created_at = Column(DateTime, default=datetime.now())
    updated_at = Column(DateTime, nullable=True)

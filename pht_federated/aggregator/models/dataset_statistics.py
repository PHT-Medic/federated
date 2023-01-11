import uuid
from datetime import datetime

from sqlalchemy import JSON, Column, DateTime, ForeignKey, Integer, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from pht_federated.aggregator.db.base_class import Base


class DatasetStatistics(Base):
    __tablename__ = "dataset_statistics"
    id = Column(UUID(as_uuid=True), primary_key=True, index=True, default=uuid.uuid4)
    discovery_id = Column(Integer, ForeignKey("data_discovery.id", ondelete="CASCADE"))
    discovery = relationship("DataDiscovery", back_populates="dataset_statistics")
    client_id = Column(String, nullable=True)
    statistics = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=datetime.now())
    updated_at = Column(DateTime, nullable=True)

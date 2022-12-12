from datetime import datetime

from sqlalchemy import Column, Integer, JSON, DateTime, String, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from pht_federated.aggregator.db.base_class import Base


class DataDiscovery(Base):
    __tablename__ = "data_discovery"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=True)
    proposal_id = Column(UUID, ForeignKey('proposals.id', ondelete="CASCADE"))
    created_at = Column(DateTime, default=datetime.now())
    updated_at = Column(DateTime, nullable=True)
    proposal = relationship("Proposal", back_populates="discoveries")
    query = Column(JSON, nullable=True)
    dataset_statistics = relationship("DatasetStatistics", back_populates="discovery", cascade="all, delete, delete-orphan")

class DiscoverySummary(Base):
    __tablename__ = "discovery_summary"
    id = Column(Integer, primary_key=True, index=True)
    proposal_id = Column(Integer, default=0)
    station_id = Column(Integer, default=0)
    item_count = Column(Integer, default=0)
    feature_count = Column(Integer, default=0)
    data_information = Column(JSON, default={})

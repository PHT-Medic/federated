from datetime import datetime
import uuid

from sqlalchemy import Column, Integer, JSON, DateTime, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from pht_federated.aggregator.db.base_class import Base

class Proposal(Base):
    __tablename__ = "proposals"
    id = Column(UUID(as_uuid=True), primary_key=True, index=True, default=uuid.uuid4, unique=True)
    name = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.now())
    updated_at = Column(DateTime, nullable=True)
    discoveries = relationship("DataDiscovery", back_populates="proposal", cascade="all, delete, delete-orphan", lazy="dynamic")
    protocols = relationship("AggregationProtocol", back_populates="proposal", cascade="all, delete, delete-orphan", lazy="dynamic")



from pht_federated.aggregator.db.base_class import Base
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, JSON
from sqlmodel import Field
from datetime import datetime
import uuid as uuid_pkg


class DatasetStatistics(Base):
    __tablename__ = "dataset_statistics"
    #id = Column(String, primary_key=True, default=uuid.uuid4())
    #id: uuid_pkg.UUID = Field(
    #    default_factory=uuid_pkg.uuid4,
    #    primary_key=True,
    #    index=True,
    #    nullable=False,
    #)
    id = Column(Integer, primary_key=True, index=True)
    proposal_id = Column(Integer, ForeignKey('proposals.proposal_id'), index=True)
    # proposal_id = Column(Integer, default=0)
    item_count = Column(Integer, default=0)
    feature_count = Column(Integer, default=0)
    column_information = Column(JSON, default={})


class Proposals(Base):
    __tablename__ = "proposals"
    #id = Column(String, primary_key=True, default=uuid.uuid4())
    #id: uuid_pkg.UUID = Field(
    #    default_factory=uuid_pkg.uuid4,
    #    primary_key=True,
    #    index=True,
    #    nullable=False,
    #)
    proposal_id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True)
    created_at = Column(DateTime, default=datetime.now())
    updated_at = Column(DateTime, nullable=True)

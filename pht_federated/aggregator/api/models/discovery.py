from sqlalchemy import Column, Integer, JSON

from pht_federated.aggregator.db.base_class import Base

from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, JSON
from sqlalchemy.dialects.postgresql import UUID

import uuid

from datetime import datetime


class DataSetSummary(Base):
    __tablename__ = "datasets_summary"
    id = Column(Integer, primary_key=True, index=True)
    proposal_id = Column(Integer, default=0)
    item_count = Column(Integer, default=0)
    feature_count = Column(Integer, default=0)
    data_information = Column(JSON, default={})


'''class DataSet(Base):
    __tablename__ = "discoveries"
    id = Column(UUID(as_uuid=True), primary_key=True, index=True, default=uuid.uuid4)
    created_at = Column(DateTime, default=datetime.now())
    updated_at = Column(DateTime, nullable=True)
    proposal_id = Column(String, nullable=True)
    name = Column(String)
    data_type = Column(String, nullable=True)
    storage_type = Column(String, nullable=True)
    access_path = Column(String, nullable=True)
    fhir_server = Column(Integer, ForeignKey('fhir_servers.id'), nullable=True)
    summary = Column(JSON, nullable=True)
    # trains = relationship("Train", back_populates="dataset")
    
    class FHIRServer(Base):
    __tablename__ = "fhir_servers"
    id = Column(Integer, primary_key=True, index=True)
    api_address = Column(String)
    name = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.now())
    updated_at = Column(DateTime, nullable=True)
    username = Column(String, nullable=True)
    password = Column(String, nullable=True)
    client_id = Column(String, nullable=True)
    client_secret = Column(String, nullable=True)
    oidc_provider_url = Column(String, nullable=True)
    token = Column(String)
    active = Column(Boolean, default=True)
    type = Column(String, nullable=True)
    proposal_id = Column(String, nullable=True)
    
    '''


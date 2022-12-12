from datetime import datetime

from sqlalchemy import Column, Integer, JSON, String, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from pht_federated.aggregator.db.base_class import Base


class AggregationProtocol(Base):
    __tablename__ = "aggregation_protocols"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True)
    created_at = Column(DateTime, default=datetime.now())
    updated_at = Column(DateTime, nullable=True)
    proposal_id = Column(ForeignKey('proposals.id', ondelete="CASCADE"), nullable=True)
    proposal = relationship("Proposal", back_populates="aggregation_protocols")


class ProtocolRound(Base):
    __tablename__ = "protocol_rounds"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True)
    created_at = Column(DateTime, default=datetime.now())
    updated_at = Column(DateTime, nullable=True)
    aggregation_protocol_id = Column(ForeignKey('aggregation_protocols.id', ondelete="CASCADE"), nullable=True)
    aggregation_protocol = relationship("AggregationProtocol", back_populates="protocol_rounds")
    round_number = Column(Integer, default=0)



class ClientKeyBroadcast(Base):
    __tablename__ = "client_key_broadcasts"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True)
    client_id = Column(String)
    created_at = Column(DateTime, default=datetime.now())
    updated_at = Column(DateTime, nullable=True)
    round_id = Column(ForeignKey('protocol_rounds.id', ondelete="CASCADE"), nullable=True)
    round = relationship("ProtocolRound", back_populates="client_key_broadcasts")
    cipher_public_key = Column(String)
    sharing_public_key = Column(String)
    key_signature = Column(String, nullable=True)




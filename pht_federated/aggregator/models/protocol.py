import uuid
from datetime import datetime

from sqlalchemy import (
    JSON,
    Boolean,
    Column,
    DateTime,
    Enum,
    ForeignKey,
    Integer,
    String,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from pht_federated.aggregator.db.base_class import Base

status_options = ("initialized", "active", "inactive", "finished", "cancelled")

status_enum = Enum(*status_options, name="status")


class AggregationProtocol(Base):
    __tablename__ = "aggregation_protocols"
    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        index=True,
        default=uuid.uuid4,
        unique=True,
    )
    name = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.now())
    status = Column(status_enum, default="initialized")
    updated_at = Column(DateTime, nullable=True)
    proposal_id = Column(ForeignKey("proposals.id", ondelete="CASCADE"), nullable=True)
    proposal = relationship("Proposal", back_populates="protocols")
    rounds = relationship(
        "ProtocolRound", back_populates="protocol", cascade="all, delete, delete-orphan"
    )
    discovery_id = Column(
        ForeignKey("data_discovery.id", ondelete="CASCADE"), nullable=True
    )
    discovery = relationship("DataDiscovery", back_populates="protocols")
    settings = relationship(
        "ProtocolSettings",
        back_populates="protocol",
        uselist=False,
        cascade="all, delete, delete-orphan",
    )
    num_rounds = Column(Integer, default=0)
    active_round = Column(Integer, nullable=True)


class ProtocolSettings(Base):
    __tablename__ = "protocol_settings"
    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        index=True,
        default=uuid.uuid4,
        unique=True,
    )
    protocol_id = Column(
        ForeignKey("aggregation_protocols.id", ondelete="CASCADE"), nullable=False
    )
    protocol = relationship("AggregationProtocol", back_populates="settings")
    auto_advance = Column(Boolean, default=False)
    auto_advance_min = Column(Integer, default=5)
    min_participants = Column(Integer, default=3)


class ProtocolRound(Base):
    __tablename__ = "protocol_rounds"
    id = Column(Integer, primary_key=True, index=True)
    round = Column(Integer, default=0)
    protocol_id = Column(
        ForeignKey("aggregation_protocols.id", ondelete="CASCADE"), nullable=True
    )
    protocol = relationship("AggregationProtocol", back_populates="rounds")
    step = Column(Integer, default=0)
    client_key_broadcasts = relationship(
        "ClientKeyBroadcast",
        back_populates="round",
        cascade="all, delete, delete-orphan",
    )
    client_key_shares = relationship(
        "ClientKeyShares", back_populates="round", cascade="all, delete, delete-orphan"
    )
    created_at = Column(DateTime, default=datetime.now())
    updated_at = Column(DateTime, nullable=True)


class ClientKeyBroadcast(Base):
    __tablename__ = "client_key_broadcasts"
    id = Column(Integer, primary_key=True, index=True)
    client_id = Column(String)
    created_at = Column(DateTime, default=datetime.now())
    round_id = Column(ForeignKey("protocol_rounds.id", ondelete="CASCADE"))
    round = relationship("ProtocolRound", back_populates="client_key_broadcasts")
    cipher_public_key = Column(String)
    sharing_public_key = Column(String)
    key_signature = Column(String, nullable=True)


class ClientKeyShares(Base):
    __tablename__ = "client_key_shares"
    id = Column(Integer, primary_key=True, index=True)
    client_id = Column(String)
    created_at = Column(DateTime, default=datetime.now())
    round_id = Column(ForeignKey("protocol_rounds.id", ondelete="CASCADE"))
    round = relationship("ProtocolRound", back_populates="client_key_shares")
    ciphers = Column(JSON)

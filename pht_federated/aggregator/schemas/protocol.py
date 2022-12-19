from typing import Optional, Union, List
from datetime import datetime
import uuid

from pydantic import BaseModel

from pht_federated.aggregator.schemas.discovery import DataDiscovery
from pht_federated.aggregator.schemas.proposal import Proposal
from pht_federated.protocol.models.client_messages import ShareKeysMessage, ClientKeyBroadCast

class ProtocolRound(BaseModel):
    id: int
    step: int
    client_key_broadcasts: Optional[List[ClientKeyBroadCast]]
    client_key_shares: Optional[List[ShareKeysMessage]]
    created_at: datetime
    updated_at: Optional[datetime]
    protocol_id: Optional[Union[uuid.UUID, str]]
    class Config:
        orm_mode = True


class AggregationProtocolBase(BaseModel):
    name: Optional[str]
    proposal_id: Optional[Union[uuid.UUID, str]]
    discovery_id: Optional[Union[uuid.UUID, int, str]]


class AggregationProtocolCreate(AggregationProtocolBase):
    pass


class AggregationProtocolUpdate(AggregationProtocolBase):
    pass


class AggregationProtocol(AggregationProtocolBase):
    id: Optional[Union[uuid.UUID, str]]
    created_at: Optional[datetime]
    updated_at: Optional[datetime]
    proposal: Optional[Proposal]
    discovery: Optional[DataDiscovery]
    rounds: Optional[List[ProtocolRound]]
    num_rounds: int
    class Config:
        orm_mode = True





import uuid
from datetime import datetime
from typing import List, Optional, Union

from pydantic import BaseModel

from pht_federated.aggregator.schemas.discovery import DataDiscovery
from pht_federated.aggregator.schemas.proposal import Proposal
from pht_federated.protocols.secure_aggregation.models.client_messages import (
    ClientKeyBroadCast,
    ShareKeysMessage,
)


class ProtocolSettingsBase(BaseModel):
    """
    Protocol settings
    """

    auto_advance: Optional[bool] = False
    auto_advance_min: Optional[int] = 5
    min_participants: Optional[int] = 3


class ProtocolSettingsCreate(ProtocolSettingsBase):
    pass


class ProtocolSettingsUpdate(ProtocolSettingsBase):
    pass


class ProtocolSettings(ProtocolSettingsBase):
    id: Union[str, uuid.UUID, int]
    protocol_id: Union[str, uuid.UUID, int]

    class Config:
        orm_mode = True


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
    active_round: Optional[int]
    settings: Optional[ProtocolSettings]

    class Config:
        orm_mode = True


class RoundStatus(BaseModel):
    step: Optional[int] = None
    registered: Optional[int] = 0
    key_shares: Optional[int] = 0
    masked_inputs: Optional[int] = 0
    unmask_shares: Optional[int] = 0


class ProtocolStatus(BaseModel):
    protocol_id: Optional[Union[uuid.UUID, str]]
    status: str
    num_rounds: Optional[int] = 0
    active_round: Optional[int] = None
    round_status: RoundStatus

    class Config:
        orm_mode = True


class RegistrationResponse(BaseModel):
    protocol_id: Union[uuid.UUID, str]
    round_id: Union[int, str]
    message: Optional[str]
    currently_registered: int

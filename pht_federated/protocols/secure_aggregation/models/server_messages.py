import uuid
from typing import List, Optional, Union

from pydantic import BaseModel

from pht_federated.protocols.secure_aggregation.models import HexString
from pht_federated.protocols.secure_aggregation.models.client_messages import (
    ClientKeyBroadCast,
)


class BroadCastClientKeys(BaseModel):
    client_id: Union[int, str]
    broadcast: ClientKeyBroadCast


class ServerKeyBroadcast(BaseModel):
    """
    Broadcast the keys of users registered in round 1 of the protocol.
    """

    protocol_id: Union[uuid.UUID, str]
    round_id: Union[int, str]
    participants: List[BroadCastClientKeys]


class UserCipher(BaseModel):
    """
    Broadcast the ciphers of users registered in round 1 of the protocol.
    """

    sender: Union[int, str]
    receiver: Union[int, str]
    cipher: HexString


class ServerCipherBroadcast(BaseModel):
    ciphers: List[UserCipher]


class Round4Participant(BaseModel):
    """
    Broadcast the ciphers of users registered in round 1 of the protocol.
    """

    user_id: Union[int, str]
    signature: Optional[HexString] = None


class ServerUnmaskBroadCast(BaseModel):
    """
    Broadcast the participants of round 4 of the protocol to the users
    """

    participants: List[Round4Participant]


class AggregatedParameters(BaseModel):
    """
    Broadcast the aggregated parameters of the protocol to the users
    """

    params: List[float]

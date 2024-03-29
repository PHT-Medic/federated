from typing import List

import numpy as np
from pydantic import BaseModel

from pht_federated.protocols.secure_aggregation.models import HexString


class KeyShare(BaseModel):
    """
    A key share for a participant
    """

    shamir_index: int
    segments: List[HexString]


class SeedShare(BaseModel):
    """
    A seed share for a participant
    """

    shamir_index: int
    seed: HexString


class SecretShares(BaseModel):
    key_shares: List[KeyShare]
    seed_shares: List[SeedShare]


class Cipher(BaseModel):
    """
    A cipher for a participant
    """

    sender: str
    recipient: str
    seed_share: SeedShare
    key_share: KeyShare


class EncryptedCipher(BaseModel):
    """
    An encrypted cipher for a participant
    """

    recipient: str
    cipher: HexString


class SharedMask(BaseModel):
    """
    A shared mask for a participant
    """

    sender: str
    recipient: str
    mask: np.ndarray

    class Config:
        arbitrary_types_allowed = True

from typing import List

from sqlalchemy.orm import Session

from pht_federated.aggregator.models import protocol as models
from pht_federated.protocols.secure_aggregation.models.client_messages import (
    ShareKeysMessage,
)


def store_key_shares(
    db: Session, key_shares: ShareKeysMessage, round_id: int
) -> models.ClientKeyShares:
    """
    Store key shares from a client in the database for given round
    :param db:
    :param key_shares:
    :param round_id:
    :return:
    """
    db_key_shares = models.ClientKeyShares(
        **key_shares.dict(exclude_none=True), round_id=round_id
    )
    db.add(db_key_shares)
    db.commit()

    return db_key_shares


def get_key_shares_for_round(
    db: Session, round_id: int
) -> List[models.ClientKeyShares]:
    return (
        db.query(models.ClientKeyShares)
        .filter(
            models.ClientKeyShares.round_id == round_id,
        )
        .all()
    )

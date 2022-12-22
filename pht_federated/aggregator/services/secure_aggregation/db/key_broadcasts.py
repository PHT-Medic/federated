from typing import List

from sqlalchemy.orm import Session

from pht_federated.aggregator.models import protocol as models
from pht_federated.protocols.secure_aggregation.models.client_messages import (
    ClientKeyBroadCast,
)


def get_key_broadcasts_for_round(
    db: Session, round_id: int
) -> List[models.ClientKeyBroadcast]:
    return (
        db.query(models.ClientKeyBroadcast)
        .filter(
            models.ClientKeyBroadcast.round_id == round_id,
        )
        .all()
    )


def store_key_broadcast(
    db: Session,
    round: models.ProtocolRound,
    key_broadcast: ClientKeyBroadCast,
):
    """
    Store a key broadcast in the database for the given
    :param db:
    :param round:
    :param key_broadcast:
    :return:
    """
    db_broadcast = models.ClientKeyBroadcast(
        round_id=round.id, **key_broadcast.dict(exclude_none=True)
    )
    db.add(db_broadcast)
    db.commit()

from datetime import datetime
from typing import Union

from sqlalchemy.orm import Session

from pht_federated.aggregator.models.protocol import AggregationProtocol, ProtocolRound


def start_new_round(
    db: Session, db_protocol: AggregationProtocol, activate=True
) -> ProtocolRound:
    """
    Start a new round for the given protocol
    :param db: sqlalchemy session
    :param db_protocol: the protocol to start a new round for
    :param activate: if True, the new round will be activated
    :return: the protocol round object
    """

    # create a new round with incremented round number
    db_round = ProtocolRound(
        protocol_id=db_protocol.id,
        round=db_protocol.num_rounds + 1,
    )
    db.add(db_round)
    db.commit()
    db.refresh(db_round)

    # update the protocol with the new round number
    db_protocol.num_rounds += 1
    if activate:
        db_protocol.active_round = db_round.id
    db_protocol.updated_at = datetime.now()

    db.add(db_protocol)
    db.commit()
    db.refresh(db_protocol)
    return db_round


def get_next_round(
    db: Session, protocol: AggregationProtocol
) -> Union[ProtocolRound, None]:
    """
    Get the next round of the given protocol or return None if no next round exists
    :param db: sqlalchemy session
    :param protocol: protocol object
    :return: next round
    """

    active_round = get_active_round(db, protocol)
    if active_round:
        db_round = (
            db.query(ProtocolRound)
            .filter(
                ProtocolRound.protocol_id == protocol.id,
                ProtocolRound.round == active_round.round + 1,
            )
            .first()
        )
        return db_round
    return None


def get_active_round(
    db: Session, protocol: AggregationProtocol
) -> Union[ProtocolRound, None]:
    """
    Get the active round of the given protocol or return None if no active round exists
    :param db: sqlalchemy session
    :param protocol: protocol object
    :return: active round
    """
    return db.get(ProtocolRound, protocol.active_round)

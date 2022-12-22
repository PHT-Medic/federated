from sqlalchemy.orm import Session

from pht_federated.aggregator.models import protocol as models
from pht_federated.aggregator.services.secure_aggregation import logging
from pht_federated.aggregator.services.secure_aggregation.db.key_broadcasts import (
    get_key_broadcasts_for_round,
)


def update_protocol_on_registration(
    db: Session, protocol: models.AggregationProtocol
) -> models.ProtocolRound:
    """
    Update the protocol status on a client registration
    :param db: sqlalchemy session
    :param protocol: protocol object
    :return: updated protocol status
    """
    settings: models.ProtocolSettings = protocol.settings
    active_round = db.get(models.ProtocolRound, protocol.active_round)

    if active_round.step == 0:
        key_broadcasts = get_key_broadcasts_for_round(db, active_round.id)
        if settings.auto_advance and len(key_broadcasts) >= settings.auto_advance_min:
            logging.protocol_info(
                protocol.id,
                f"Auto advancing round {active_round.id} to step 1 - Key sharing",
            )
            active_round.step = 1
            db.add(active_round)
            db.commit()
            db.refresh(active_round)
            return active_round

    else:
        raise ValueError("Protocol is already in the next step")

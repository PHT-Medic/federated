from loguru import logger
from sqlalchemy.orm import Session

from pht_federated.aggregator.models import protocol as models
from pht_federated.aggregator.schemas import protocol as schemas
from pht_federated.aggregator.services.secure_aggregation import logging
from pht_federated.aggregator.services.secure_aggregation.db import rounds
from pht_federated.aggregator.services.secure_aggregation.db.key_broadcasts import (
    get_key_broadcasts_for_round,
    store_key_broadcast,
)
from pht_federated.aggregator.services.secure_aggregation.db.key_shares import (
    store_key_shares,
    get_key_shares_for_round,
)
from pht_federated.aggregator.services.secure_aggregation.steps import registration
from pht_federated.protocols.secure_aggregation.models.client_messages import (
    ClientKeyBroadCast,
    ShareKeysMessage,
)

from pht_federated.protocols.secure_aggregation.models.server_messages import (
    ServerKeyBroadcast,
)
from pht_federated.protocols.secure_aggregation.server.server_protocol import (
    ServerProtocol,
)


class SecureAggregation:
    """
    Service to manage Server side functions of the secure aggregation protocol
    """

    def __init__(self):
        self.protocol = ServerProtocol()

    def advance_round(
        self, db: Session, protocol: models.AggregationProtocol
    ) -> schemas.ProtocolRound:
        """
        Advance the current round of the given protocol
        :param db: sqlalchemy session
        :param protocol: protocol object
        :return: updated protocol status
        """
        current_round = rounds.get_active_round(db, protocol)
        if not current_round:
            raise ValueError("No active round found")

        if self._check_advance_requirements(db, protocol, current_round):
            logging.protocol_info(
                protocol.id,
                f"Advancing round {current_round.round} from step {current_round.step} "
                f"to step {current_round.step + 1}",
            )
            if protocol.status != "active":
                protocol.status = "active"
                db.add(protocol)
            current_round.step += 1
            db.add(current_round)
            db.commit()
            db.refresh(current_round)
            return current_round
        else:
            logging.protocol_error(
                protocol.id,
                f"Round {current_round.round} step {current_round.step} requirements not met",
            )
            raise ValueError("Advancement requirements not met")

    def _check_advance_requirements(
        self,
        db: Session,
        protocol: models.AggregationProtocol,
        db_round: models.ProtocolRound,
    ) -> bool:
        """
        Check if the requirements for advancing to the next round are met
        :param db: sqlalchemy session
        :param protocol: protocol object
        :param db_round: round object
        :return:
        """
        settings: models.ProtocolSettings = protocol.settings

        if db_round.step == 0:
            # check if the minimum number of key broadcasts is reached
            return (
                len(get_key_broadcasts_for_round(db, db_round.id))
                >= settings.min_participants
            )

        elif db_round.step == 1:
            raise NotImplementedError("Not implemented yet")

        elif db_round.step == 2:
            raise NotImplementedError("Not implemented yet")

        elif db_round.step == 3:
            raise NotImplementedError("Not implemented yet")

        else:
            raise ValueError("Invalid step number")

    def start_new_round(
        self, db: Session, db_protocol: models.AggregationProtocol, activate=True
    ) -> models.ProtocolRound:
        """
        Start a new round for the given protocol
        :param db: sqlalchemy session
        :param db_protocol: the protocol to start a new round for
        :param activate: if True, the new round will be activated
        :return: the protocol round object
        """

        db_round = rounds.start_new_round(db, db_protocol, activate)
        logger.info(
            f"Protocol - {db_protocol.id} - Starting new round ({db_round.round})"
        )
        return db_round

    def process_registration(
        self,
        db: Session,
        key_broadcast: ClientKeyBroadCast,
        protocol: models.AggregationProtocol,
    ) -> schemas.RegistrationResponse:

        """
        Process a client registration, if no round exists or the registration for the current round is closed, a new
        round will be started with the client submission.

        :param db: sqlalchemy session
        :param key_broadcast: key broadcast message from the client
        :param protocol: protocol object
        :return:
        """
        db_round = rounds.get_active_round(db, protocol)

        # if no round exists and the protocol is not finished or cancelled, start a new round
        if not db_round and protocol.status not in ["finished", "cancelled"]:
            logging.protocol_warning(
                protocol.id, "No active round found. Creating new round"
            )
            db_round = rounds.start_new_round(db, protocol, activate=True)

        # if the round is not in registration phase, start a new round or register to existing next round
        if db_round.step != 0:

            next_round = rounds.get_next_round(db, protocol)
            if next_round:
                logging.protocol_warning(
                    protocol.id,
                    "Registration already finished. Registering for next round.",
                )
            else:

                next_round = rounds.start_new_round(db, protocol, activate=False)
                logging.protocol_warning(
                    protocol.id,
                    f"Registration for round already finished. Creating new round ({db_round.round})",
                )
            # store the key broadcast
            store_key_broadcast(db, next_round, key_broadcast)

            next_round_participants = get_key_broadcasts_for_round(db, next_round.id)

            response = schemas.RegistrationResponse(
                round_id=next_round.id,
                protocol_id=protocol.id,
                message=f"Registration for current round closed. Registered for the next round {next_round.round}",
                currently_registered=len(next_round_participants),
            )

        else:
            # store the key broadcast
            store_key_broadcast(db, db_round, key_broadcast)
            participants = get_key_broadcasts_for_round(db, db_round.id)
            logging.protocol_info(
                protocol.id,
                f"Registered client no. {len(participants)} for round {db_round.round}",
            )
            response = schemas.RegistrationResponse(
                round_id=db_round.id,
                protocol_id=protocol.id,
                message="Successfully registered for round {}".format(db_round.round),
                currently_registered=len(participants),
            )

            registration.update_protocol_on_registration(db, protocol)

        return response

    def protocol_status(
        self, db: Session, protocol: models.AggregationProtocol, round_id: int = None
    ) -> schemas.ProtocolStatus:

        # get selected or currently active round
        current_round = db.get(
            models.ProtocolRound, round_id if round_id else protocol.active_round
        )
        if not current_round:
            raise ValueError("No active round found")
        logging.protocol_info(
            protocol.id,
            f"Status: {protocol.status}, Current round: {current_round.round}",
        )

        key_broadcasts = get_key_broadcasts_for_round(db, current_round.id)
        # get the round status
        round_status = schemas.RoundStatus(
            step=current_round.step,
            registered=len(key_broadcasts),
        )

        # get the protocol status
        status = schemas.ProtocolStatus(
            protocol_id=protocol.id,
            status=protocol.status,
            num_rounds=protocol.num_rounds,
            active_round=protocol.active_round,
            round_status=round_status,
        )
        logging.protocol_debug(
            protocol.id, f"Protocol status: \n{status.json(indent=2)}"
        )
        return status

    def get_key_broadcasts(
        self, db: Session, protocol: models.AggregationProtocol
    ) -> ServerKeyBroadcast:
        """
        Get all key broadcasts for the given protocol
        :param db: sqlalchemy session
        :param protocol: protocol object
        :return:
        """

        current_round = rounds.get_active_round(db, protocol)
        if not current_round:
            raise ValueError("No active round found")

        key_broadcasts = get_key_broadcasts_for_round(db, current_round.id)

        server_broad_cast = ServerKeyBroadcast(
            protocol_id=protocol.id,
            round_id=current_round.id,
            participants=key_broadcasts,
        )

        return server_broad_cast

    def process_key_shares(
        self,
        db: Session,
        key_shares: ShareKeysMessage,
        protocol: models.AggregationProtocol,
    ):
        """
        Process a list of key shares
        :param db: sqlalchemy session
        :param key_shares: list of key shares
        :return:
        """

        db_round = rounds.get_active_round(db, protocol)
        if not db_round:
            raise ValueError("No active round found")
        if db_round.step != 1:
            raise ValueError("Invalid round step")

        # store the key shares
        db_share = store_key_shares(db, key_shares, db_round.id)

        # check if the requirements for advancing to the next round are met
        if self._check_advance_requirements(db, protocol, db_round):
            self.advance_round(db, protocol)

        key_shares = get_key_shares_for_round(db, db_round.id)
        logger.info(
            f"Protocol - {protocol.id} - Received {len(key_shares)} key shares for round {db_round.round}"
        )

        response = schemas.KeyShareResponse(
            round_id=db_round.id,
            message=f"Successfully submitted key shares for round {db_round.round}",
            protocol_id=protocol.id,
            key_shares_submitted=len(key_shares),
        )
        return response


secure_aggregation = SecureAggregation()

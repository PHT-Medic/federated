from datetime import datetime
from typing import Union

from sqlalchemy.orm import Session

from pht_federated.aggregator.models import protocol as models
from pht_federated.aggregator.schemas import protocol as schemas
from pht_federated.aggregator.services.secure_aggregation import logging
from pht_federated.aggregator.services.secure_aggregation.db.key_broadcasts import (
    get_key_broadcasts_for_round,
)
from pht_federated.protocols.secure_aggregation.models.client_messages import (
    ClientKeyBroadCast,
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

    def update_protocol_on_client_input(
        self, db: Session, protocol: models.AggregationProtocol
    ):

        settings: models.ProtocolSettings = protocol.settings
        active_round = self._get_active_round(db, protocol)

        if active_round.step == 0:
            key_broadcasts = get_key_broadcasts_for_round(db, active_round.id)
            if (
                settings.auto_advance
                and len(key_broadcasts) >= settings.auto_advance_min
            ):
                logging.protocol_info(
                    protocol.id,
                    f"Auto advancing round {active_round.id} to step 1 - Key sharing",
                )
                self.advance_round(db, protocol)

        else:
            raise NotImplementedError("Not implemented yet")

    def advance_round(
        self, db: Session, protocol: models.AggregationProtocol
    ) -> schemas.ProtocolRound:
        """
        Advance the current round of the given protocol
        :param db: sqlalchemy session
        :param protocol: protocol object
        :return: updated protocol status
        """
        current_round = self._get_active_round(db, protocol)
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
            logging.protocol_warning(
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

        # create a new round with incremented round number
        db_round = models.ProtocolRound(
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
        db_round = self._get_active_round(db, protocol)

        # if no round exists and the protocol is not finished or cancelled, start a new round
        if not db_round and protocol.status not in ["finished", "cancelled"]:
            logging.protocol_warning(
                protocol.id, "No active round found. Creating new round"
            )
            db_round = self.start_new_round(db, protocol, activate=True)

        # if the round is not in registration phase, start a new round or register to existing next round
        if db_round.step != 0:

            next_round = self._get_next_round(db, protocol)
            if next_round:
                logging.protocol_warning(
                    protocol.id,
                    "Registration already finished. Registering for next round.",
                )
                db_round = next_round
            else:

                db_round = self.start_new_round(db, protocol, activate=True)
                logging.protocol_warning(
                    protocol.id,
                    f"Registration for round already finished. Creating new round ({db_round.round})",
                )

        db_broadcast = models.ClientKeyBroadcast(
            round_id=db_round.id, **key_broadcast.dict(exclude_none=True)
        )
        db.add(db_broadcast)
        db.commit()

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

        return response

    def protocol_status(
        self, db: Session, protocol: models.AggregationProtocol, round_id: int = None
    ) -> schemas.ProtocolStatus:
        current_round = self._get_round(
            db, round_number=round_id if round_id else protocol.active_round
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

    def _get_active_round(
        self, db: Session, protocol: models.AggregationProtocol
    ) -> models.ProtocolRound:
        current_round = self._get_round(db, protocol.active_round)
        return current_round

    def _get_next_round(
        self, db: Session, protocol: models.AggregationProtocol
    ) -> models.ProtocolRound:
        next_round = self._get_round(db, protocol.num_rounds + 1)
        return next_round

    def _get_previous_round(
        self, db: Session, protocol: models.AggregationProtocol
    ) -> Union[None, models.ProtocolRound]:

        if protocol.num_rounds == 0:
            return None

        previous_round = self._get_round(db, protocol.num_rounds - 1)
        return previous_round

    @staticmethod
    def _get_round(db: Session, round_number: int) -> models.ProtocolRound:
        db_round = (
            db.query(models.ProtocolRound)
            .filter(models.ProtocolRound.id == round_number)
            .first()
        )
        return db_round


secure_aggregation = SecureAggregation()

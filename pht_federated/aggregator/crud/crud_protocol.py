from datetime import datetime
from typing import List, Optional, Union

from sqlalchemy.orm import Session

from pht_federated.aggregator.crud.base import CRUDBase
from pht_federated.aggregator.models import protocol
from pht_federated.aggregator.schemas import protocol as schemas
from pht_federated.protocols.secure_aggregation.models.client_messages import ShareKeysMessage, ClientKeyBroadCast
from pht_federated.aggregator.crud import crud_discovery, crud_proposals


class CRUDProtocol(
    CRUDBase[protocol.AggregationProtocol, schemas.AggregationProtocolCreate, schemas.AggregationProtocolUpdate]):

    def validate_create_update(
            self,
            db: Session,
            *,
            obj_in: Union[schemas.AggregationProtocolCreate, schemas.AggregationProtocolUpdate]
    ) -> schemas.AggregationProtocolCreate:

        # validate discovery
        if obj_in.discovery_id:
            db_discovery = crud_discovery.discoveries.get(db, obj_in.discovery_id)
            if not db_discovery:
                raise ValueError("Invalid discovery id")

        # validate proposal
        if obj_in.proposal_id:
            db_proposal = crud_proposals.proposals.get(db, obj_in.proposal_id)
            if not db_proposal:
                raise ValueError("Invalid proposal id")

        return obj_in

    def get_for_proposal(
            self,
            db: Session,
            proposal_id: str,
            skip: int = 0,
            limit: int = 100) -> List[protocol.AggregationProtocol]:
        return db.query(self.model).filter(self.model.proposal_id == proposal_id).offset(skip).limit(limit).all()

    def get_for_discovery(
            self,
            db: Session,
            discovery_id: str,
            skip: int = 0,
            limit: int = 100) -> List[protocol.AggregationProtocol]:
        return db.query(self.model).filter(self.model.discovery_id == discovery_id).offset(skip).limit(limit).all()


    def add_client_key_broadcast(self,
                                 db: Session,
                                 *,
                                 db_round: protocol.ProtocolRound,
                                 client_key_broadcast: ClientKeyBroadCast) -> protocol.ProtocolRound:
        pass

protocols = CRUDProtocol(protocol.AggregationProtocol)

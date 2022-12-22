from typing import List, Union

from fastapi.encoders import jsonable_encoder
from sqlalchemy.orm import Session

from pht_federated.aggregator.crud import crud_discovery, crud_proposals
from pht_federated.aggregator.crud.base import CreateSchemaType, CRUDBase
from pht_federated.aggregator.models import protocol
from pht_federated.aggregator.schemas import protocol as schemas


class CRUDProtocol(
    CRUDBase[
        protocol.AggregationProtocol,
        schemas.AggregationProtocolCreate,
        schemas.AggregationProtocolUpdate,
    ]
):
    def create(
        self, db: Session, *, obj_in: CreateSchemaType
    ) -> protocol.AggregationProtocol:
        db_protocol = super().create(db, obj_in=obj_in)
        # Create default settings for the protocol
        settings = protocol.ProtocolSettings()
        settings.protocol_id = db_protocol.id
        db.add(settings)
        db.commit()
        db.refresh(db_protocol)
        return db_protocol

    def validate_create_update(
        self,
        db: Session,
        *,
        obj_in: Union[
            schemas.AggregationProtocolCreate, schemas.AggregationProtocolUpdate
        ],
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
        self, db: Session, proposal_id: str, skip: int = 0, limit: int = 100
    ) -> List[protocol.AggregationProtocol]:
        return (
            db.query(self.model)
            .filter(self.model.proposal_id == proposal_id)
            .offset(skip)
            .limit(limit)
            .all()
        )

    def get_for_discovery(
        self, db: Session, discovery_id: str, skip: int = 0, limit: int = 100
    ) -> List[protocol.AggregationProtocol]:
        return (
            db.query(self.model)
            .filter(self.model.discovery_id == discovery_id)
            .offset(skip)
            .limit(limit)
            .all()
        )

    def update_proposal_settings(
        self,
        db: Session,
        *,
        db_obj: protocol.AggregationProtocol,
        obj_in: schemas.ProtocolSettingsUpdate,
    ) -> protocol.AggregationProtocol:

        db_settings = db_obj.settings
        obj_data = jsonable_encoder(db_settings)

        update_data = obj_in.dict(exclude_unset=True)
        for field in obj_data:
            if field in update_data:
                setattr(db_obj.settings, field, update_data[field])

        db.add(db_settings)
        db.commit()
        db.refresh(db_settings)
        return db_settings


protocols = CRUDProtocol(protocol.AggregationProtocol)

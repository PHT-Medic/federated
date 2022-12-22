from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from pht_federated.aggregator.api import dependencies
from pht_federated.aggregator.crud.crud_discovery import discoveries
from pht_federated.aggregator.crud.crud_proposals import proposals
from pht_federated.aggregator.crud.crud_protocol import protocols
from pht_federated.aggregator.schemas.protocol import (
    AggregationProtocol,
    AggregationProtocolCreate,
    AggregationProtocolUpdate,
    RegistrationResponse,
    ProtocolSettings,
    ProtocolSettingsUpdate,
)
from pht_federated.aggregator.services.secure_aggregation.service import (
    secure_aggregation,
)
from pht_federated.protocols.secure_aggregation.models import client_messages

router = APIRouter()


@router.post("", response_model=AggregationProtocol)
def create_protocol(
    protocol_create: AggregationProtocolCreate,
    db: Session = Depends(dependencies.get_db),
) -> AggregationProtocol:
    try:
        protocols.validate_create_update(db, obj_in=protocol_create)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

    protocol_create = protocols.create(db, obj_in=protocol_create)
    return protocol_create


@router.get("", response_model=List[AggregationProtocol])
def read_protocols(
    skip: int = 0,
    limit: int = 100,
    discovery_id: str = None,
    proposal_id: str = None,
    db: Session = Depends(dependencies.get_db),
) -> List[AggregationProtocol]:
    if discovery_id:
        discovery = discoveries.get(db, discovery_id)
        if not discovery:
            raise HTTPException(
                status_code=404, detail=f"Discovery - {discovery_id} - not found"
            )
        query = protocols.get_for_discovery(
            db, discovery_id=discovery_id, skip=skip, limit=limit
        )
    elif proposal_id:
        proposal = proposals.get(db, proposal_id)
        if not proposal:
            raise HTTPException(
                status_code=404, detail=f"Proposal - {proposal_id} - not found"
            )
        query = protocols.get_for_proposal(
            db, proposal_id=proposal_id, skip=skip, limit=limit
        )
    else:
        query = protocols.get_multi(db, skip=skip, limit=limit)
    return query


@router.get("/{protocol_id}", response_model=AggregationProtocol)
def get_protocol(
    protocol_id: str, db: Session = Depends(dependencies.get_db)
) -> AggregationProtocol:
    protocol = protocols.get(db, protocol_id)
    if not protocol:
        raise HTTPException(
            status_code=404, detail=f"Protocol - {protocol_id} - not found"
        )
    return protocol


@router.put("/{protocol_id}", response_model=AggregationProtocol)
def update_protocol(
    protocol_id: str,
    protocol_update: AggregationProtocolUpdate,
    db: Session = Depends(dependencies.get_db),
) -> AggregationProtocol:
    protocol = protocols.get(db, protocol_id)
    if not protocol:
        raise HTTPException(
            status_code=404, detail=f"Protocol - {protocol_id} - not found"
        )

    try:
        protocols.validate_create_update(db, obj_in=protocol_update)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    protocol = protocols.update(db, db_obj=protocol, obj_in=protocol_update)
    return protocol


@router.delete("/{protocol_id}", response_model=AggregationProtocol)
def delete_protocol(
    protocol_id: str, db: Session = Depends(dependencies.get_db)
) -> AggregationProtocol:
    protocol = protocols.get(db, protocol_id)
    if not protocol:
        raise HTTPException(
            status_code=404, detail=f"Protocol - {protocol_id} - not found"
        )
    protocol = protocols.remove(db, id=protocol_id)
    return protocol


@router.get("/{protocol_id}/status")
def get_protocol_status(
    protocol_id: str, db: Session = Depends(dependencies.get_db)
) -> dict:
    protocol = protocols.get(db, protocol_id)
    if not protocol:
        raise HTTPException(
            status_code=404, detail=f"Protocol - {protocol_id} - not found"
        )

    status = secure_aggregation.protocol_status(protocol, db)
    return status


@router.get("/{protocol_id}/settings", response_model=ProtocolSettings)
def get_protocol_settings(
    protocol_id: str, db: Session = Depends(dependencies.get_db)
) -> dict:
    protocol = protocols.get(db, protocol_id)
    if not protocol:
        raise HTTPException(
            status_code=404, detail=f"Protocol - {protocol_id} - not found"
        )

    settings = protocol.settings
    return settings


@router.put("/{protocol_id}/settings", response_model=ProtocolSettings)
def update_protocol_settings(
    protocol_id: str,
    settings_update: ProtocolSettingsUpdate,
    db: Session = Depends(dependencies.get_db),
) -> dict:
    protocol = protocols.get(db, protocol_id)
    if not protocol:
        raise HTTPException(
            status_code=404, detail=f"Protocol - {protocol_id} - not found"
        )

    settings = protocols.update_proposal_settings(
        db, db_obj=protocol, obj_in=settings_update
    )
    return settings


@router.post("/{protocol_id}/register", response_model=RegistrationResponse)
def register_for_protocol(
    protocol_id: str,
    key_broadcast: client_messages.ClientKeyBroadCast,
    db: Session = Depends(dependencies.get_db),
) -> RegistrationResponse:
    protocol = protocols.get(db, protocol_id)
    if not protocol:
        raise HTTPException(
            status_code=404, detail=f"Protocol - {protocol_id} - not found"
        )

    try:
        response = secure_aggregation.process_registration(db, key_broadcast, protocol)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    return response

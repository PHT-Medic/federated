from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from loguru import logger

from pht_federated.aggregator.api import dependencies
from pht_federated.aggregator.schemas.protocol import AggregationProtocol, AggregationProtocolCreate, \
    AggregationProtocolUpdate

from pht_federated.aggregator.crud.crud_protocol import protocols
from pht_federated.aggregator.crud.crud_proposals import proposals
from pht_federated.aggregator.crud.crud_discovery import discoveries

router = APIRouter()


@router.post("", response_model=AggregationProtocol)
def create_protocol(protocol_create: AggregationProtocolCreate,
                    db: Session = Depends(dependencies.get_db)) -> AggregationProtocol:
    try:
        checks = protocols.validate_create_update(db, obj_in=protocol_create)
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
        db: Session = Depends(dependencies.get_db)) -> List[AggregationProtocol]:
    if discovery_id:
        discovery = discoveries.get(db, discovery_id)
        if not discovery:
            raise HTTPException(status_code=404, detail=f"Discovery - {discovery_id} - not found")
        query = protocols.get_for_discovery(db, discovery_id=discovery_id, skip=skip, limit=limit)
    elif proposal_id:
        proposal = proposals.get(db, proposal_id)
        if not proposal:
            raise HTTPException(status_code=404, detail=f"Proposal - {proposal_id} - not found")
        query = protocols.get_for_proposal(db, proposal_id=proposal_id, skip=skip, limit=limit)
    else:
        query = protocols.get_multi(db, skip=skip, limit=limit)
    return query


@router.get("/{protocol_id}", response_model=AggregationProtocol)
def get_protocol(protocol_id: str, db: Session = Depends(dependencies.get_db)) -> AggregationProtocol:
    protocol = protocols.get(db, protocol_id)
    if not protocol:
        raise HTTPException(status_code=404, detail=f"Protocol - {protocol_id} - not found")
    return protocol


@router.put("/{protocol_id}", response_model=AggregationProtocol)
def update_protocol(protocol_id: str, protocol_update: AggregationProtocolUpdate,
                    db: Session = Depends(dependencies.get_db)) -> AggregationProtocol:
    protocol = protocols.get(db, protocol_id)
    if not protocol:
        raise HTTPException(status_code=404, detail=f"Protocol - {protocol_id} - not found")

    try:
        checks = protocols.validate_create_update(db, obj_in=protocol_update)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    protocol = protocols.update(db, db_obj=protocol, obj_in=protocol_update)
    return protocol


@router.delete("/{protocol_id}", response_model=AggregationProtocol)
def delete_protocol(protocol_id: str, db: Session = Depends(dependencies.get_db)) -> AggregationProtocol:
    protocol = protocols.get(db, protocol_id)
    if not protocol:
        raise HTTPException(status_code=404, detail=f"Protocol - {protocol_id} - not found")
    protocol = protocols.remove(db, id=protocol_id)
    return protocol

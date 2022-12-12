from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from pht_federated.aggregator.api import dependencies
from pht_federated.aggregator.api.schemas.proposal import ProposalCreate, ProposalUpdate, Proposal
from pht_federated.aggregator.api.crud.crud_proposals import proposals

router = APIRouter()


@router.post("", response_model=ProposalCreate)
def create_proposal(proposal: ProposalCreate, db: Session = Depends(dependencies.get_db)) -> ProposalCreate:
    proposal = proposals.create(db, obj_in=proposal)
    return proposal


@router.get("", response_model=List[Proposal])
def read_proposals(skip: int = 0, limit: int = 100, db: Session = Depends(dependencies.get_db)) -> List[Proposal]:
    query = proposals.get_multi(db, skip=skip, limit=limit)
    return query


@router.get("/{proposal_id}", response_model=Proposal)
def get_proposal(proposal_id: str, db: Session = Depends(dependencies.get_db)) -> Proposal:
    proposal = proposals.get(db, proposal_id)
    if not proposal:
        raise HTTPException(status_code=404, detail=f"Proposal - {proposal_id} - not found")
    return proposal


@router.put("/{proposal_id}", response_model=Proposal)
def update_proposal(proposal_id: str, proposal: ProposalUpdate, db: Session = Depends(dependencies.get_db)) -> Proposal:
    proposal = proposals.update(db, db_obj=proposal, obj_in=proposal)
    return proposal


@router.delete("/{proposal_id}", response_model=Proposal)
def delete_proposal(proposal_id: str, db: Session = Depends(dependencies.get_db)) -> Proposal:
    proposal = proposals.delete(db, proposal_id)
    return proposal

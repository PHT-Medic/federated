from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from pht_federated.aggregator.api import dependencies
from pht_federated.aggregator.crud.crud_proposals import proposals
from pht_federated.aggregator.schemas.proposal import (Proposal,
                                                       ProposalCreate,
                                                       ProposalUpdate)

router = APIRouter()


@router.post("", response_model=ProposalCreate)
def create_proposal(
    proposal: ProposalCreate, db: Session = Depends(dependencies.get_db)
) -> ProposalCreate:
    if proposals.get(db=db, id=proposal.id):
        raise HTTPException(
            status_code=400, detail=f"Proposal with id {proposal.id} already exists"
        )
    proposal = proposals.create(db, obj_in=proposal)
    return proposal


@router.get("", response_model=List[Proposal])
def read_proposals(
    skip: int = 0, limit: int = 100, db: Session = Depends(dependencies.get_db)
) -> List[Proposal]:
    query = proposals.get_multi(db, skip=skip, limit=limit)
    return query


@router.get("/{proposal_id}", response_model=Proposal)
def get_proposal(
    proposal_id: str, db: Session = Depends(dependencies.get_db)
) -> Proposal:
    proposal = proposals.get(db, proposal_id)
    if not proposal:
        raise HTTPException(
            status_code=404, detail=f"Proposal - {proposal_id} - not found"
        )
    return proposal


@router.put("/{proposal_id}", response_model=Proposal)
def update_proposal(
    proposal_id: str,
    proposal: ProposalUpdate,
    db: Session = Depends(dependencies.get_db),
) -> Proposal:
    db_proposal = proposals.get(db, proposal_id)
    if not db_proposal:
        raise HTTPException(
            status_code=404, detail=f"Proposal - {proposal_id} - not found"
        )

    proposal = proposals.update(db, db_obj=db_proposal, obj_in=proposal)
    return proposal


@router.delete("/{proposal_id}", response_model=Proposal)
def delete_proposal(
    proposal_id: str, db: Session = Depends(dependencies.get_db)
) -> Proposal:
    db_proposal = proposals.get(db, proposal_id)
    if not db_proposal:
        raise HTTPException(
            status_code=404, detail=f"Proposal - {proposal_id} - not found"
        )
    proposal = proposals.remove(db, id=proposal_id)
    return proposal

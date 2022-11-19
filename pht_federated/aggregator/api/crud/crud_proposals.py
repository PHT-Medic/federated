from sqlalchemy.orm import Session
from fastapi import Depends
from typing import Any, List
from .base import CRUDBase, CreateSchemaType, ModelType, Optional
from pht_federated.aggregator.api.models.dataset_statistics import Proposals
from pht_federated.aggregator.api.schemas.proposals import ProposalsCreate, ProposalsUpdate
from pht_federated.aggregator.api import dependencies
from uuid import uuid4


class CRUDProposals(CRUDBase[Proposals, ProposalsCreate, ProposalsUpdate]):

    def get_all_by_proposal_id(self, proposal_id: uuid4, db: Session = Depends(dependencies.get_db)) -> List[Proposals]:
        proposal = db.query(Proposals).filter(Proposals.proposal_id == proposal_id).all()
        return proposal

    def delete_by_proposal_id(self, proposal_id: uuid4, db: Session = Depends(dependencies.get_db)) -> Proposals:
        proposal_del = db.query(Proposals).filter(Proposals.id == proposal_id).delete()
        return proposal_del


proposals = CRUDProposals(Proposals)

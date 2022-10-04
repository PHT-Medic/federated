from sqlalchemy.orm import Session
from fastapi import Depends
from typing import Any, List
from .base import CRUDBase, CreateSchemaType, ModelType, Optional
from pht_federated.aggregator.api.models.dataset_statistics import Proposals
from pht_federated.aggregator.api.schemas.proposals import ProposalsCreate, ProposalsUpdate
from .. import dependencies


class CRUDProposals(CRUDBase[Proposals, ProposalsCreate, ProposalsUpdate]):


    def get_all_by_proposal_id(self, proposal_id: int, db: Session = Depends(dependencies.get_db)) -> List[Proposals]:
        dataset = db.query(Proposals).filter(Proposals.proposal_id == proposal_id).all()
        return dataset

    def delete_by_proposal_id(self, proposal_id: int, db: Session = Depends(dependencies.get_db)) -> Proposals:
        dataset_del = db.query(Proposals).filter(Proposals.proposal_id == proposal_id).delete()
        return dataset_del


proposals = CRUDProposals(Proposals)

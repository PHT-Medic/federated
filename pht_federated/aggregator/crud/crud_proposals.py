from sqlalchemy.orm import Session
from fastapi import Depends
from typing import Any, List
from .base import CRUDBase, CreateSchemaType, ModelType, Optional
from pht_federated.aggregator.models.proposal import Proposal
from pht_federated.aggregator.schemas.proposal import ProposalCreate, ProposalUpdate
from pht_federated.aggregator.api import dependencies
from uuid import uuid4


class CRUDProposals(CRUDBase[Proposal, ProposalCreate, ProposalUpdate]):
    pass

proposals = CRUDProposals(Proposal)

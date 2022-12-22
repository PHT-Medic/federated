from pht_federated.aggregator.models.proposal import Proposal
from pht_federated.aggregator.schemas.proposal import ProposalCreate, ProposalUpdate

from .base import CRUDBase


class CRUDProposals(CRUDBase[Proposal, ProposalCreate, ProposalUpdate]):
    pass


proposals = CRUDProposals(Proposal)

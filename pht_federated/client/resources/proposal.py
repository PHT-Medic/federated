
from pht_federated.aggregator.schemas.proposal import (
    Proposal,
    ProposalCreate,
    ProposalUpdate,
)
from pht_federated.client.resource_client import ResourceClient


class ProposalClient(ResourceClient[Proposal, ProposalCreate, ProposalUpdate]):
    pass

import typing

from pht_federated.client.resource_client import ResourceClient
from pht_federated.aggregator.schemas.proposal import ProposalCreate, ProposalUpdate, Proposal


class ProposalClient(ResourceClient[Proposal, ProposalCreate, ProposalUpdate]):
    pass

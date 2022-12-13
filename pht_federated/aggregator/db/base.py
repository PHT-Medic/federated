# Import all the models, so that Base has them before being
# imported by Alembic
from pht_federated.aggregator.db.base_class import Base  # noqa
from pht_federated.aggregator.models.proposal import Proposal  # noqa
from pht_federated.aggregator.models.dataset_statistics import DatasetStatistics  # noqa
from pht_federated.aggregator.models.discovery import DataDiscovery, DiscoverySummary  # noqa
from pht_federated.aggregator.models.protocol import (AggregationProtocol, ProtocolRound, ClientKeyBroadcast,
                                                          ClientKeyShares)  # noqa

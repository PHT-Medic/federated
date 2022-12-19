from .base import CRUDBase
from typing import List
from pht_federated.aggregator.models.discovery import DataDiscovery
from pht_federated.aggregator.schemas.discovery import DataDiscoveryCreate, DataDiscoveryUpdate


class CRUDDiscovery(CRUDBase[DataDiscovery, DataDiscoveryCreate, DataDiscoveryUpdate]):
    pass

discoveries = CRUDDiscovery(DataDiscovery)

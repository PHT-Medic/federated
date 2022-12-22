from pht_federated.aggregator.models.discovery import DataDiscovery
from pht_federated.aggregator.schemas.discovery import (DataDiscoveryCreate,
                                                        DataDiscoveryUpdate)

from .base import CRUDBase


class CRUDDiscovery(CRUDBase[DataDiscovery, DataDiscoveryCreate, DataDiscoveryUpdate]):
    pass


discoveries = CRUDDiscovery(DataDiscovery)

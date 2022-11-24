# Import all the models, so that Base has them before being
# imported by Alembic
from pht_federated.aggregator.storage.db.base_class import Base  # noqa

import pytest
from pht_federated.aggregator.storage.db.setup import setup_database
from pht_federated.aggregator.storage.db import schemas


def test_setup_db():
    setup_database()

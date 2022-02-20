import pytest
from aggregator.storage.setup import setup_database
from aggregator.storage import schemas


def test_setup_db():
    setup_database()

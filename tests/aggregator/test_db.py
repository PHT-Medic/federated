import pytest
from aggregator.db.setup import setup_database
from aggregator.db import schemas

def test_setup_db():
    setup_database()
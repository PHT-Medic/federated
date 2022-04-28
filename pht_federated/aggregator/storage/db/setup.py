from sqlmodel import SQLModel
from pht_federated.aggregator.storage.db.engine import engine
from pht_federated.aggregator import *  # register schemas to metadata


def setup_database():
    SQLModel.metadata.create_all(engine)

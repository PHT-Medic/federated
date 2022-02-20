from sqlmodel import SQLModel
from aggregator.storage.db.engine import engine
from aggregator.storage.db.schemas import *  # register schemas to metadata


def setup_database():
    SQLModel.metadata.create_all(engine)

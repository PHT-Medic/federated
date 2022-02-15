from sqlmodel import SQLModel
from aggregator.db import engine

def setup_database():
    SQLModel.metadata.create_all(engine)

from typing import Generator
from pht_federated.aggregator.storage.db.engine import SessionLocal
import os




def get_db() -> Generator:
    try:
        db = SessionLocal()
        yield db
    finally:
        db.close()




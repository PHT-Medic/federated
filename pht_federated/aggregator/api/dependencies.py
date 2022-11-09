from typing import Generator
from pht_federated.aggregator.storage.db.engine import SessionLocal


def get_db() -> Generator:
    try:
        db = SessionLocal()
        yield db
    finally:
        db.close()

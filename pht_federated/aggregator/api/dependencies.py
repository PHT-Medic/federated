from typing import Generator
from pht_federated.aggregator.db.session import SessionLocal

import os
from fastapi.security import HTTPBearer



def get_db() -> Generator:
    try:
        db = SessionLocal()
        yield db
    finally:
        db.close()


def fernet_key() -> bytes:
    # load fernet key from environment variables
    fernet_key = os.getenv("FERNET_KEY")
    if not fernet_key:
        # TODO load key from station config file
        pass
    return fernet_key.encode()



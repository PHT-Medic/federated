import os
from sqlmodel import SQLModel
from dotenv import load_dotenv, find_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from pht_federated.aggregator.db.base_class import Base

# Create new sqlite database for testing

# load the .env file
load_dotenv(find_dotenv())

SQLALCHEMY_DATABASE_URL = os.getenv("TEST_DB", "sqlite:///./test.db")

if SQLALCHEMY_DATABASE_URL.startswith("sqlite"):
    engine = create_engine(
        SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
    )
else:
    engine = create_engine(SQLALCHEMY_DATABASE_URL)

TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

#Base.metadata.drop_all(bind=engine)
Base.metadata.create_all(bind=engine)
'''SQLModel.metadata.create_all(engine)
engine.execute('CREATE TABLE "datasets_summary" ('
               'PRIMARY KEY (id)'
               'proposal_id INTEGER,'
               'name VARCHAR, '
               'data_information JSON);')'''


def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

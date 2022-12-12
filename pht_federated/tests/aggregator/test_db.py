import os
from dotenv import load_dotenv, find_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from pht_federated.aggregator.db.base_class import Base

# Create new sqlite database for testing

# load the .env file
load_dotenv(find_dotenv())

if os.getenv("FEDERATED_TEST_DB"):
    SQLALCHEMY_DATABASE_URL = os.getenv('FEDERATED_TEST_DB')
else:
    SQLALCHEMY_DATABASE_URL = "postgresql+psycopg2://test:test@localhost:5442/test_db"

if SQLALCHEMY_DATABASE_URL.startswith("sqlite"):
    engine = create_engine(
        SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
    )
else:
    engine = create_engine(SQLALCHEMY_DATABASE_URL)

TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base.metadata.drop_all(bind=engine)
Base.metadata.create_all(bind=engine)


def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

from sqlmodel import create_engine
from sqlalchemy.orm import sessionmaker
import os
from dotenv import load_dotenv, find_dotenv
from pht_federated.aggregator.db.base_class import Base

load_dotenv(find_dotenv())

# SQLALCHEMY_DATABASE_URL = "sqlite:///./app.db"

if os.getenv("FEDERATED_DEV_DB"):
    SQLALCHEMY_DATABASE_URL = os.getenv('FEDERATED_DEV_DB')
else:
    SQLALCHEMY_DATABASE_URL = "postgresql+psycopg2://admin:admin@localhost:5452/dev_db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,  # connect_args={"check_same_thread": False}  For sqlite db
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base.metadata.drop_all(bind=engine)
Base.metadata.create_all(bind=engine)
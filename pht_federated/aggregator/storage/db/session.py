import os

from dotenv import find_dotenv, load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

load_dotenv(find_dotenv())


if os.getenv("AGGREGATOR_DB"):
    SQLALCHEMY_DATABASE_URL = os.getenv("AGGREGATOR_DB")
else:
    SQLALCHEMY_DATABASE_URL = "postgresql+psycopg2://admin:admin@localhost:5452/dev_db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,  # connect_args={"check_same_thread": False}  For sqlite db
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

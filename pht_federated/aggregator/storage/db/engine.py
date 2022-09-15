from sqlmodel import create_engine
from sqlalchemy.orm import sessionmaker


ENGINE_URL = 'postgresql+psycopg2://postgres:postgres@localhost/postgres'

ENGINE_URL = "postgresql+psycopg2://admin:admin@localhost:5442/pht_station"

engine = create_engine(ENGINE_URL)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

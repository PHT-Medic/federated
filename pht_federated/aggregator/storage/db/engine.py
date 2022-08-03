from sqlmodel import create_engine

ENGINE_URL = 'postgresql+psycopg2://postgres:postgres@localhost/postgres'

ENGINE_URL = "postgresql+psycopg2://admin:admin@localhost:5442/pht_station"

engine = create_engine(ENGINE_URL)

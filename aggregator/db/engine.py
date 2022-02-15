from sqlmodel import create_engine

ENGINE_URL = 'postgresql+psycopg2://postgres:postgres@localhost/postgres'

engine = create_engine(ENGINE_URL)

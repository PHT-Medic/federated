from pht_federated.aggregator.storage.db.session import engine
from pht_federated.aggregator.db.base import Base


def setup_db():
    Base.metadata.create_all(bind=engine)


def reset_db():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)


if __name__ == '__main__':
    # Base.metadata.drop_all(bind=engine)
    setup_db()

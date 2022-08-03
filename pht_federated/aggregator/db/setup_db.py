import uuid

from pht_federated.aggregator.db.session import engine, SessionLocal
from pht_federated.aggregator.db.base import Base

#from pht_federated.aggregator.api.models.discovery import DataSetSummary, DataSet
from pht_federated.aggregator.api.models import discovery


def setup_db(dev=False):
    Base.metadata.create_all(bind=engine)
    if dev:
        seed_db_for_testing()


def reset_db(dev=False):
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)

    if dev:
        seed_db_for_testing()


def seed_db_for_testing():
    session = SessionLocal()
    # create docker trains
    if not session.query(discovery.DataSet).all():

        dts = []
        for _ in range(3):
            dt = discovery.DataSet(
                proposal_id=str(uuid.uuid4()),

            )
            dts.append(dt)
        session.add_all(dts)
        session.commit()

    session.close()


if __name__ == '__main__':
    # Base.metadata.drop_all(bind=engine)
    setup_db()

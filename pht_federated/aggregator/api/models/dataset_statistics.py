from pht_federated.aggregator.db.base_class import Base

from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, JSON



class DatasetStatistics(Base):
    __tablename__ = "dataset_statistics"
    id = Column(Integer, primary_key=True, index=True)
    #proposal_id = Column(Integer, ForeignKey('proposal.id'))
    proposal_id = Column(Integer, default=0)
    item_count = Column(Integer, default=0)
    feature_count = Column(Integer, default=0)
    column_information = Column(JSON, default={})


class Proposals(Base):
    __tablename__ = "proposals"
    id = Column(Integer, primary_key=True, index=True)

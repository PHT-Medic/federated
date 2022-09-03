from pht_federated.aggregator.db.base_class import Base

from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, JSON



class DatasetStatistics(Base):
    __tablename__ = "dataset_statistcs"
    id = Column(Integer, primary_key=True, index=True)
    proposal_id = Column(Integer, default=0)
    n_items = Column(Integer, default=0)
    n_features = Column(Integer, default=0)
    column_information = Column(JSON, default={})



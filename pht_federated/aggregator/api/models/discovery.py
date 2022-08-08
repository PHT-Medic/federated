from sqlalchemy import Column, Integer, JSON

from pht_federated.aggregator.db.base_class import Base

from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, JSON
from sqlalchemy.dialects.postgresql import UUID

import uuid

from datetime import datetime


class DataSetSummary(Base):
    __tablename__ = "datasets_summary"
    id = Column(Integer, primary_key=True, index=True)
    proposal_id = Column(Integer, default=0)
    item_count = Column(Integer, default=0)
    feature_count = Column(Integer, default=0)
    data_information = Column(JSON, default={})


class DataSetFigure(Base):
    __tablename__ = "datasets_plot"
    id = Column(Integer, primary_key=True, index=True)
    plot_id = Column(Integer, default=0)
    fig_data = Column(JSON, default={})



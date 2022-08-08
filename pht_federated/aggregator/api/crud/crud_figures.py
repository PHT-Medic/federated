from sqlalchemy.orm import Session
from fastapi import APIRouter, Depends, HTTPException
from .base import CRUDBase, CreateSchemaType, ModelType, Optional
from fastapi.encoders import jsonable_encoder
from pht_federated.aggregator.api.models.discovery import DataSetFigure
from pht_federated.aggregator.api.schemas.discovery import SummaryCreate, SummaryUpdate, FigureData, DataSetFigure, FigureCreate, FigureUpdate
from pht_federated.aggregator.api.endpoints import dependencies
import plotly, json


class CRUDFigures(CRUDBase[DataSetFigure, FigureCreate, FigureUpdate]):

    def create(self, db: Session = Depends(dependencies.get_db), *, obj_in: CreateSchemaType) -> Optional[ModelType]:
        obj_in_data = jsonable_encoder(obj_in)
        db_obj = self.model(**obj_in_data)
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)

        return db_obj

    #def get_by_discovery_id(self, proposal_id: int, db: Session = Depends(dependencies.get_db)) -> DataSetSummary:
    #    discovery = db.query(DataSetSummary).filter(DataSetSummary.proposal_id == proposal_id).first()
    #    return discovery

    def create_plot(self, db: Session = Depends(dependencies.get_db), *, obj_in: DataSetFigure) -> Optional[ModelType]:
        obj_in_data = jsonable_encoder(obj_in)
        db_obj_plot = self.model(**obj_in_data)
        print("DB OBJ PLOT : {}".format(db_obj_plot))
        db.add(db_obj_plot)
        db.commit()
        db.refresh(db_obj_plot)

        return db_obj_plot


figures = CRUDFigures(DataSetFigure)

from sqlalchemy.orm import Session
from fastapi import APIRouter, Depends, HTTPException
from .base import CRUDBase, CreateSchemaType, ModelType, Optional
from fastapi.encoders import jsonable_encoder
from pht_federated.aggregator.api.models.discovery import DataSetSummary
from pht_federated.aggregator.api.schemas.discovery import SummaryCreate, SummaryUpdate, FigureData, DataSetFigure
from pht_federated.aggregator.api.endpoints import dependencies
import plotly, json


class CRUDDiscoveries(CRUDBase[DataSetSummary, SummaryCreate, SummaryUpdate]):

    def create(self, db: Session = Depends(dependencies.get_db), *, obj_in: CreateSchemaType) -> Optional[ModelType]:
        obj_in_data = jsonable_encoder(obj_in)
        db_obj = self.model(**obj_in_data)
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)

        return db_obj


    def create_plot(self, db: Session = Depends(dependencies.get_db), *, obj_in: DataSetFigure) -> Optional[ModelType]:
        obj_in_data = jsonable_encoder(obj_in)
        db_obj_plot = self.model(**obj_in_data)
        print("DB OBJ PLOT : {}".format(db_obj_plot))
        db.add(db_obj_plot)
        db.commit()
        db.refresh(db_obj_plot)

        return db_obj_plot


discoveries = CRUDDiscoveries(DataSetSummary)

from pydantic import BaseModel, Field
from typing import Optional, List


class FigureData(BaseModel):
    layout: dict
    data: list

class FeatureData(BaseModel):
    feature_name: str
    figure: Optional[FigureData]

class DiscoveryFigure(BaseModel):
    fig_data: Optional[FeatureData]

    class Config:
        orm_mode = True


class FigureCreate(DiscoveryFigure):
    pass


class FigureUpdate(DiscoveryFigure):
    pass


class DiscoveryFigures(BaseModel):
    fig_data_all: Optional[List[DiscoveryFigure]]

    class Config:
        orm_mode = True
from pydantic import BaseModel, Field
from typing import Optional, List


class FigureData(BaseModel):
    feature_name: str
    layout: dict
    data: list


class DiscoveryFigure(BaseModel):
    fig_data: Optional[FigureData]

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
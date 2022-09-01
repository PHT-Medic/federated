from pydantic import BaseModel, Field
from typing import Optional, List


class FigureData(BaseModel):
    layout: dict
    data: list

class DiscoveryFigure(BaseModel):
    feature_name: Optional[str]
    figure: Optional[FigureData]

class FigureCreate(DiscoveryFigure):
    pass


class FigureUpdate(DiscoveryFigure):
    pass


class DiscoveryFigures(BaseModel):
    fig_data_all: Optional[List[DiscoveryFigure]]

    class Config:
        orm_mode = True
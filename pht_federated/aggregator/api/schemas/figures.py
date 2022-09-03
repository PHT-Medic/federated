from pydantic import BaseModel, Field
from typing import Optional, List


class FigureData(BaseModel):
    data: list
    layout: dict

class DiscoveryFigure(BaseModel):
    title: Optional[str]
    type: Optional[str]
    figure: Optional[FigureData]

class FigureCreate(DiscoveryFigure):
    pass


class FigureUpdate(DiscoveryFigure):
    pass


class DiscoveryFigures(BaseModel):
    fig_data_all: Optional[List[DiscoveryFigure]]

    class Config:
        orm_mode = True
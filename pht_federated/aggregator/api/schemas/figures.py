from pydantic import BaseModel, Field
from typing import Optional


class FigureData(BaseModel):
    layout: dict
    data: list


class DiscoveryFigure(BaseModel):
    fig_data: Optional[FigureData]


class FigureCreate(DiscoveryFigure):
    pass


class FigureUpdate(DiscoveryFigure):
    pass
from typing import List, Optional

from pydantic import BaseModel


class FigureData(BaseModel):
    data: list
    layout: dict


class DiscoveryFigure(BaseModel):
    title: Optional[str]
    type: Optional[str]
    figure: Optional[FigureData]


class DiscoveryFigures(BaseModel):
    fig_data_all: Optional[List[DiscoveryFigure]]

    class Config:
        orm_mode = True

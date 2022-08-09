from typing_extensions import Annotated
from enum import Enum


from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, Any, List, Union, Dict, Literal
from typing_extensions import Annotated
from enum import Enum
from pht_federated.aggregator.api.schemas.figures import *



class DiscoveryColumn(BaseModel):
    title: Optional[str]
    not_na_elements: Optional[int]
    figure: Optional[DiscoveryFigure]


class DiscoveryUniqueColumn(DiscoveryColumn):
    type: Literal['unique']
    number_of_duplicates: Optional[int]


class DiscoveryEqualColumn(DiscoveryColumn):
    type: Literal['equal']
    value: Optional[str]


class DiscoveryCategoricalColumn(DiscoveryColumn):
    type: Literal['categorical']
    number_categories: Optional[int]
    value_counts: Optional[Dict[str, int]]
    most_frequent_element: Optional[Union[int, str]]
    frequency: Optional[int]


class DiscoveryNumericalColumn(DiscoveryColumn):
    type: Literal['numeric']
    mean: Optional[float]
    std: Optional[float]
    min: Optional[float]
    max: Optional[float]


class DiscoveryStatistics(BaseModel):
    n_items: Optional[int] = 0
    n_features: Optional[int] = 0
    column_information: Optional[List[Annotated[Union[DiscoveryCategoricalColumn,
                                                      DiscoveryNumericalColumn,
                                                      DiscoveryEqualColumn,
                                                      DiscoveryUniqueColumn],
                                                Field(discriminator='type')]]]

    class Config:
        orm_mode = True



class DiscoverySummary(BaseModel):
    proposal_id: Optional[int]
    item_count: Optional[int]
    feature_count: Optional[int]
    data_information: Optional[List[Annotated[Union[DiscoveryCategoricalColumn,
                                                    DiscoveryNumericalColumn],
                                              Field(discriminator='type')]]]

    class Config:
        orm_mode = True


class SummaryCreate(DiscoverySummary):
    pass


class SummaryUpdate(DiscoverySummary):
    pass




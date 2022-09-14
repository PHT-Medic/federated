from typing import Optional, Any, List, Union, Dict, Literal
from typing_extensions import Annotated
from pht_federated.aggregator.api.schemas.figures import *


class DiscoveryUniqueColumn(BaseModel):
    type: Literal['unique']
    number_of_duplicates: Optional[int]


class DiscoveryEqualColumn(BaseModel):
    type: Literal['equal']
    value: Optional[str]


class DiscoveryCategoricalColumn(BaseModel):
    type: Literal['categorical']
    title: Optional[str]
    not_na_elements: Optional[int]
    number_categories: Optional[int]
    value_counts: Optional[Dict[str, int]]
    most_frequent_element: Optional[Union[int, str]]
    frequency: Optional[int]
    figure_data: Optional[DiscoveryFigure]

class DiscoveryUnstructuredColumn(BaseModel):
    type: Literal['unstructured']
    title: Optional[str]
    not_na_elements: Optional[int]
    number_categories: Optional[int]
    value_counts: Optional[Dict[str, int]]
    most_frequent_element: Optional[Union[int, str]]
    frequency: Optional[int]
    figure_data: Optional[DiscoveryFigure]

class DiscoveryNumericalColumn(BaseModel):
    type: Literal['numeric']
    title: Optional[str]
    not_na_elements: Optional[int]
    mean: Optional[float]
    std: Optional[float]
    min: Optional[float]
    max: Optional[float]
    figure_data: Optional[DiscoveryFigure]



class DiscoverySummary(BaseModel):
    proposal_id: Optional[int]
    item_count: Optional[int]
    feature_count: Optional[int]
    data_information: Optional[List[Annotated[Union[DiscoveryCategoricalColumn,
                                                    DiscoveryNumericalColumn,
                                                    DiscoveryUnstructuredColumn,
                                                    DiscoveryEqualColumn,
                                                    DiscoveryUniqueColumn],
                                              Field(discriminator='type')]]]

    class Config:
        orm_mode = True


class SummaryCreate(DiscoverySummary):
    pass


class SummaryUpdate(DiscoverySummary):
    pass



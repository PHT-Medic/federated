from pydantic import BaseModel, Field
from typing import Optional, Any, List, Union, Dict, Literal
from typing_extensions import Annotated




class DatasetUniqueColumn(BaseModel):
    type: Literal['unique']
    number_of_duplicates: Optional[int]


class DatasetEqualColumn(BaseModel):
    type: Literal['equal']
    value: Optional[str]


class DatasetCategoricalColumn(BaseModel):
    type: Literal['categorical']
    title: Optional[str]
    not_na_elements: Optional[int]
    number_categories: Optional[int]
    value_counts: Optional[Dict[str, int]]
    most_frequent_element: Optional[Union[int, str]]
    frequency: Optional[int]


class DatasetNumericalColumn(BaseModel):
    type: Literal['numeric']
    title: Optional[str]
    not_na_elements: Optional[int]
    mean: Optional[float]
    std: Optional[float]
    min: Optional[float]
    max: Optional[float]

class DatasetStatistics(BaseModel):
    n_items: Optional[int]
    n_features: Optional[int]
    column_information: Optional[List[Annotated[Union[DatasetCategoricalColumn,
                                                      DatasetNumericalColumn,
                                                      DatasetEqualColumn,
                                                      DatasetUniqueColumn],
                                                Field(discriminator='type')]]]

    class Config:
        orm_mode = True

class DiscoveryStatistics(DatasetStatistics):
    proposal_id: Optional[int]

    class Config:
        orm_mode = True


class StatisticsCreate(DiscoveryStatistics):
    pass


class StatisticsUpdate(DiscoveryStatistics):
    pass
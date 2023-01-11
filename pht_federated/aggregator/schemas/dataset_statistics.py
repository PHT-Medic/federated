import uuid
from typing import Dict, List, Literal, Optional, Union, Any

from pydantic import BaseModel, Field
from typing_extensions import Annotated
from enum import Enum

class DataType(Enum):
    """
    Enum for data types
    """
    IMAGE = "image"
    GENOME = "genome"
    FHIR = "fhir"
    CSV = "csv"
    STRUCTURED = "structured"
    UNSTRUCTURED = "unstructured"
    HYBRID = "hybrid"

class DatasetUniqueColumn(BaseModel):
    type: Literal["unique"]
    title: Optional[str]
    number_of_duplicates: Optional[int]


class DatasetEqualColumn(BaseModel):
    type: Literal["equal"]
    title: Optional[str]
    value: Optional[Union[Any]]


class DatasetCategoricalColumn(BaseModel):
    type: Literal["categorical"]
    title: Optional[str]
    not_na_elements: Optional[int]
    number_categories: Optional[int]
    value_counts: Optional[Dict[str, int]]
    most_frequent_element: Optional[Union[int, str]]
    frequency: Optional[int]


class DatasetNumericalColumn(BaseModel):
    type: Literal["numeric"]
    title: Optional[str]
    not_na_elements: Optional[int]
    mean: Optional[float]
    std: Optional[float]
    min: Optional[float]
    max: Optional[float]


class DatasetUnstructuredData(BaseModel):
    type: Literal["unstructured"]
    title: Optional[str]
    not_na_elements: Optional[int]
    number_targets: Optional[int]
    target_counts: Optional[Dict[str, int]]
    most_frequent_target: Optional[Union[int, str]]
    frequency: Optional[int]

class TabularStatistics(BaseModel):
    item_count: Optional[int]
    feature_count: Optional[int]
    column_information: Optional[
        List[
            Annotated[
                Union[
                    DatasetCategoricalColumn,
                    DatasetNumericalColumn,
                    DatasetUnstructuredData,
                    DatasetEqualColumn,
                    DatasetUniqueColumn,
                ],
                Field(discriminator="type"),
            ]
        ]
    ]


class CodeStatistics(BaseModel):
    system: Optional[str]
    code: Optional[str]
    code_statistics: Optional[TabularStatistics]


class ResourceStatistics(BaseModel):
    resource_name: Optional[str]
    resource_statistics: Optional[TabularStatistics]
    code_based_statistics: Optional[List[CodeStatistics]]


class FHIRStatistics(BaseModel):
    type: Literal['fhir']
    resource_types: Optional[List[str]]
    server_statistics: Optional[List[ResourceStatistics]]


class CSVStatistics(BaseModel):
    type: Literal['csv']
    csv_statistics: Optional[TabularStatistics]


class DatasetStatistics(BaseModel):
    statistics: Optional[List[Annotated[Union[CSVStatistics,
                                              FHIRStatistics],
                                        Field(discriminator='type')]]]
    class Config:
        orm_mode = True


class DiscoveryStatistics(DatasetStatistics):
    id: Optional[uuid.UUID]
    discovery_id: Optional[Union[int, uuid.UUID, str]]
    class Config:
        orm_mode = True


class StatisticsCreate(DiscoveryStatistics):
    pass


class StatisticsUpdate(DiscoveryStatistics):
    pass

from pydantic import BaseModel
from typing import Optional
from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, Any, List, Union, Dict, Literal
from typing_extensions import Annotated
from enum import Enum


class NumericalData(BaseModel):
    attribute_name: Optional[str]
    mean: Optional[float]
    min: Optional[float]
    max: Optional[float]


class CategoricalCount(BaseModel):
    category_value: Optional[str]
    count: Optional[int]


class CategoricalData(BaseModel):
    attribute_name: Optional[str]
    value_counts: Optional[List[CategoricalCount]]


class CategoricalDataLocal(CategoricalData):
    most_frequent_element: Optional[Union[str, int]]
    frequency: Optional[int]


class StructuredData(BaseModel):
    data_summary: Optional[List[Union[NumericalData, CategoricalData]]]


class UnstructuredData(BaseModel):
    target_counts: Optional[CategoricalCount]
    mean_size: Optional[float]


class DataSetSummary(BaseModel):
    proposal_id: Optional[int]
    count: Optional[int]
    information: Optional[Union[StructuredData, UnstructuredData]]


class DataSetStatistics(BaseModel):
    n_items: Optional[int] = 0
    n_features: Optional[int] = 0
    column_information: Optional[List[Annotated[Union[DataSetCategoricalColumn,
                                                      DataSetNumericalColumn],
                                                Field(discriminator='type')]]]

    class Config:
        orm_mode = True


class SummaryCreate(DataSetSummary):
    pass


class SummaryUpdate(DataSetSummary):
    pass


class FigureData(BaseModel):
    layout: dict
    data: list


class DataSetFigure(BaseModel):
    fig_data: Optional[FigureData]



class StorageType(Enum):
    """
    Enum for storage types
    """
    LOCAL = "local"
    MINIO = "minio"
    DB = "db"


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


class DataSetBase(BaseModel):
    name: str
    data_type: Optional[DataType] = None
    storage_type: Optional[StorageType] = None
    proposal_id: Optional[str] = None
    access_path: Optional[str] = None

    class Config:
        use_enum_values = True


class DataSetCreate(DataSetBase):
    pass


class DataSetUpdate(DataSetBase):
    pass


class DataSetFile(BaseModel):
    file_name: str
    full_path: Optional[str] = None
    size: Optional[int] = None
    updated_at: Optional[datetime] = None



class DataSetColumn(BaseModel):
    title: Optional[str]
    not_na_elements: Optional[int]
    figure: Optional[DataSetFigure]


class DataSetUniqueColumn(DataSetColumn):
    type: Literal['unique']
    number_of_duplicates: Optional[int]


class DataSetEqualColumn(DataSetColumn):
    type: Literal['equal']
    value: Optional[str]


class DataSetCategoricalColumn(DataSetColumn):
    type: Literal['categorical']
    number_categories: Optional[int]
    value_counts: Optional[Dict[str, int]]
    most_frequent_element: Optional[Union[int, str]]
    frequency: Optional[int]


class DataSetNumericalColumn(DataSetColumn):
    type: Literal['numeric']
    mean: Optional[float]
    std: Optional[float]
    min: Optional[float]
    max: Optional[float]

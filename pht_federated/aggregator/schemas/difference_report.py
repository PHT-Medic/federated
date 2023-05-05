import uuid
from typing import Dict, List, Literal, Optional, Union

from pydantic import BaseModel, Field
from typing_extensions import Annotated


class RowError(BaseModel):
    column_name: Optional[str]
    error_type: Optional[str]
    suggested_type: Optional[str]
    index: Optional[int]
    value: Optional[str]
    hint: Optional[str]


class ColumnError(BaseModel):
    column_name: Optional[str]
    error_type: Optional[str]
    suggested_name: Optional[str]
    hint: Optional[str]

class DifferenceReport(BaseModel):
    dataset: Optional[str]
    datatype: Optional[str]
    status: Optional[str]
    errors: Optional[
        List[
                Union[
                    RowError,
                    ColumnError,
                ]
            ]
        ]


class ColumnHarmonizationError(BaseModel):
    local_column_name: Optional[str]
    aggregator_column_name: Optional[str]
class ColumnHarmonizationResult(BaseModel):
    column_differences: Optional[List[ColumnHarmonizationError]]


class RowHarmonizationError(BaseModel):
    index: Optional[int]
    value: Optional[Union[int, str]]
    column_name: Optional[str]
    aggregator_column_type: Optional[str]
    most_frequent_element: Optional[str]
    most_frequent_type: Optional[str]

class RowHarmonizationResult(BaseModel):
    row_differences: Optional[List[RowHarmonizationError]]

import uuid
from typing import Dict, List, Literal, Optional, Union, Tuple

from pydantic import BaseModel, Field
from typing_extensions import Annotated


class RowError(BaseModel):
    error_type: Literal["type"]
    column_name: Optional[str]
    suggested_type: Optional[str]
    index: Optional[int]
    value: Optional[str]
    hint: Optional[str]


class ColumnError(BaseModel):
    error_type: Literal["column_name"]
    column_name: Optional[str]
    suggested_name: Optional[str]
    hint: Optional[str]

class DifferenceReport(BaseModel):
    dataset: Optional[str]
    datatype: Optional[str]
    status: Optional[str]
    errors: Optional[
        List[
            Annotated[
                Union[
                    ColumnError,
                    RowError,
                ],
                Field(discriminator="error_type")
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


class ListIntersectionReport(BaseModel):
    intersection: Optional[List[Tuple[str, str]]]
    type_differences: Optional[List[List[Tuple[str, str]]]]
    dataframe_columns: Optional[List[Tuple[str, str]]]
    aggregator_columns: Optional[List[Tuple[str, str]]]


class DifferenceReportRequirements(BaseModel):
    type_differences: Optional[List[List[Tuple[str, str]]]]
    dataframe_value_difference: Optional[List[Tuple[str, str]]]
    aggregator_value_difference: Optional[List[Tuple[str, str]]]
    matched_column_names: Optional[List[List[Union[Tuple[str, str], int]]]]
    dataset_name: Optional[str]



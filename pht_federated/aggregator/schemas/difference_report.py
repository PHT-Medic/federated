import uuid
from typing import Dict, List, Literal, Optional, Union

from pydantic import BaseModel, Field
from typing_extensions import Annotated


class DifferenceReport(BaseModel):
    dataset: Optional[str]
    datatype: Optional[str]
    status: Optional[str]
    errors: Optional[
        List[
            Annotated[
                Union[
                    RowError,
                    ColumnError,
                ], Field(discriminator="type"),
            ]
        ]
    ]


class RowError(BaseModel):
    column_name: Optional[str]
    error_type: Optional[str]
    suggested_type: Optional[str]
    row_index: Optional[int]
    row_value: Optional[str]
    hint: Optional[str]


class ColumnError(BaseModel):
    column_name: Optional[str]
    error_type: Optional[str]
    suggested_name: Optional[str]
    hint: Optional[str]


class ColumnHarmonizationResult(BaseModel):
    local_column_name: Optional[str]
    aggregator_column_name: Optional[str]


class RowHarmonizationResult(BaseModel):
    row_index: Optional[int]
    row_value: Optional[int]
    column_name: Optional[str]
    aggregator_column_type: Optional[str]

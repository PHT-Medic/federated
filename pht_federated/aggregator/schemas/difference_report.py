from typing import List, Literal, Optional, Union

from pydantic import BaseModel, Field
from typing_extensions import Annotated


class RowError(BaseModel):
    error_type: Literal["row_type_error"]
    column_name: Optional[str]
    suggested_type: Optional[str]
    index: Optional[int]
    value: Optional[str]
    hint: Optional[str]


class ColumnError(BaseModel):
    error_type: Literal["column_name_error"]
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
                Field(discriminator="error_type"),
            ]
        ]
    ]

    def row_error(self) -> List[RowError]:
        return [error for error in self.errors if error.error_type == "row_type_error"]

    def column_error(self) -> List[ColumnError]:
        return [error for error in self.errors if error.error_type == "column_name_error"]




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


class VariableTypeDifference(BaseModel):
    local_column_name: Optional[str]
    aggregator_column_name: Optional[str]
    local_column_type: Optional[str]
    aggregator_column_type: Optional[str]


class DataframeColumn(BaseModel):
    name: Optional[str]
    type: Optional[str]


class AggregatorColumn(BaseModel):
    name: Optional[str]
    type: Optional[str]


class ListIntersectionReport(BaseModel):
    intersection: Optional[List[DataframeColumn]]
    type_differences: Optional[List[VariableTypeDifference]]
    dataframe_columns: Optional[List[DataframeColumn]]
    aggregator_columns: Optional[List[AggregatorColumn]]


class MatchedColumnNames(BaseModel):
    local_column_name: Optional[str]
    aggregator_column_name: Optional[str]
    aggregator_column_type: Optional[str]
    matching_probability: Optional[int]


class DifferenceReportRequirements(BaseModel):
    type_differences: Optional[List[VariableTypeDifference]]
    dataframe_value_difference: Optional[List[DataframeColumn]]
    aggregator_value_difference: Optional[List[AggregatorColumn]]
    matched_column_names: Optional[List[MatchedColumnNames]]
    dataset_name: Optional[str]


class TypeDifference(BaseModel):
    error_type: Literal["type"]
    column_name: Optional[str]
    dataframe_type: Optional[str]
    aggregator_type: Optional[str]
    hint: Optional[str]


class DataframeValueDifference(BaseModel):
    error_type: Literal["added"]
    column_name: Optional[str]
    dataframe_type: Optional[str]
    hint: Optional[str]


class AggregatorValueDifference(BaseModel):
    error_type: Literal["missing"]
    column_name: Optional[str]
    aggregator_type: Optional[str]
    hint: Optional[str]


class ColumnNameDifference(BaseModel):
    error_type: Literal["added_name"]
    column_name: Optional[str]
    dataframe_name: Optional[str]
    aggregator_name: Optional[str]
    aggregator_type: Optional[str]
    hint: Optional[str]


class DifferenceReportBackend(BaseModel):
    dataset: Optional[str]
    datatype: Optional[str]
    status: Optional[str]
    errors: Optional[
        List[
            Annotated[
                Union[
                    TypeDifference,
                    DataframeValueDifference,
                    AggregatorValueDifference,
                    ColumnNameDifference,
                ],
                Field(discriminator="error_type"),
            ]
        ]
    ]

    def name_errors(self) -> List[ColumnNameDifference]:
        return [
            error
            for error in self.errors
            if error.error_type == "added_name"
        ]

    def type_errors(self) -> List[TypeDifference]:
        return [
            error
            for error in self.errors
            if error.error_type == "type"
        ]

    def value_errors(self) -> List[Union[DataframeValueDifference, AggregatorValueDifference]]:
        return [
            error
            for error in self.errors
            if error.error_type in ["added", "missing"]
        ]
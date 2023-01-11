from datetime import datetime
from typing import List, Optional, Union, Literal
from uuid import UUID

from pydantic import BaseModel, Field
from typing_extensions import Annotated

from pht_federated.aggregator.schemas import dataset_statistics as ds
from pht_federated.aggregator.schemas.figures import DiscoveryFigure


class DataDiscoveryBase(BaseModel):
    proposal_id: Optional[Union[UUID, str]]
    created_at: Optional[datetime]
    updated_at: Optional[datetime]
    query: Optional[dict]
    statistics: Optional[List[ds.DiscoveryStatistics]]


class DataDiscoveryCreate(DataDiscoveryBase):
    pass


class DataDiscoveryUpdate(DataDiscoveryBase):
    pass


class DataDiscovery(DataDiscoveryBase):
    id: Optional[Union[int, UUID, str]]

    class Config:
        orm_mode = True


class DiscoveryUniqueColumn(ds.DatasetUniqueColumn):
    pass


class DiscoveryEqualColumn(ds.DatasetEqualColumn):
    pass


class DiscoveryCategoricalColumn(ds.DatasetCategoricalColumn):
    figure_data: Optional[DiscoveryFigure]


class DiscoveryNumericalColumn(ds.DatasetNumericalColumn):
    figure_data: Optional[DiscoveryFigure]


class DiscoveryUnstructuredData(ds.DatasetUnstructuredData):
    figure_data: Optional[DiscoveryFigure]


class DiscoveryTabularSummary(BaseModel):
    item_count: Optional[int]
    feature_count: Optional[int]
    column_information: Optional[
        List[
            Annotated[
                Union[
                    DiscoveryCategoricalColumn,
                    DiscoveryNumericalColumn,
                    DiscoveryUnstructuredData,
                    DiscoveryEqualColumn,
                    DiscoveryUniqueColumn,
                ],
                Field(discriminator="type"),
            ]
        ]
    ]

class DiscoveryCodeSummary(BaseModel):
    system: Optional[str]
    code: Optional[str]
    code_statistics: Optional[DiscoveryTabularSummary]
class DiscoveryResourceSummary(BaseModel):
    resource_name: Optional[str]
    resource_statistics: Optional[DiscoveryTabularSummary]
    code_based_statistics: Optional[List[DiscoveryCodeSummary]]

class DiscoveryFHIRSummary(BaseModel):
    type: Literal['fhir']
    discovery_resource_types: Optional[List[str]]
    discovery_server_statistics: Optional[List[DiscoveryResourceSummary]]

class DiscoveryCSVSummary(BaseModel):
    type: Literal['csv']
    discovery_csv_summary: Optional[DiscoveryTabularSummary]


class DiscoverySummary(ds.DiscoveryStatistics):
    summary: Optional[List[Annotated[Union[DiscoveryCSVSummary,
                                        DiscoveryFHIRSummary],
                                        Field(discriminator='type')]]]

    class Config:
        orm_mode = True


class SummaryCreate(DiscoverySummary):
    pass


class SummaryUpdate(DiscoverySummary):
    pass

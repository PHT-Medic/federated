from typing import Optional, Any, List, Union, Dict, Literal
from typing_extensions import Annotated
from pht_federated.aggregator.schemas.figures import *
from pht_federated.aggregator.schemas.dataset_statistics import *
from uuid import UUID
from datetime import datetime


class DataDiscoveryBase(BaseModel):
    proposal_id: Optional[Union[UUID, str]]
    created_at: Optional[datetime]
    updated_at: Optional[datetime]
    query: Optional[dict]
    statistics: Optional[List[DiscoveryStatistics]]

class DataDiscoveryCreate(DataDiscoveryBase):
    pass


class DataDiscoveryUpdate(DataDiscoveryBase):
    pass


class DataDiscovery(DataDiscoveryBase):
    id: Optional[Union[int, UUID, str]]

    class Config:
        orm_mode = True


class DiscoveryUniqueColumn(DatasetUniqueColumn):
    pass


class DiscoveryEqualColumn(DatasetEqualColumn):
    pass


class DiscoveryCategoricalColumn(DatasetCategoricalColumn):
    figure_data: Optional[DiscoveryFigure]


class DiscoveryNumericalColumn(DatasetNumericalColumn):
    figure_data: Optional[DiscoveryFigure]


class DiscoveryUnstructuredData(DatasetUnstructuredData):
    figure_data: Optional[DiscoveryFigure]


class DiscoverySummary(DiscoveryStatistics):
    column_information: Optional[List[Annotated[Union[DiscoveryCategoricalColumn,
    DiscoveryNumericalColumn,
    DiscoveryUnstructuredData,
    DiscoveryEqualColumn,
    DiscoveryUniqueColumn],
    Field(discriminator='type')]]]

    class Config:
        orm_mode = True


class SummaryCreate(DiscoverySummary):
    pass


class SummaryUpdate(DiscoverySummary):
    pass

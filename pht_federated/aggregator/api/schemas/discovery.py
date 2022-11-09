from typing import Optional, Any, List, Union, Dict, Literal
from typing_extensions import Annotated
from pht_federated.aggregator.api.schemas.figures import *
from pht_federated.aggregator.api.schemas.dataset_statistics import *


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

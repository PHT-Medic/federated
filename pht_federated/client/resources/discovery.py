import typing
from uuid import UUID

from fastapi.encoders import jsonable_encoder
from httpx import Client

from pht_federated.aggregator.schemas import discovery as schemas
from pht_federated.aggregator.schemas.dataset_statistics import StatisticsCreate, StatisticsUpdate, DiscoveryStatistics


class DiscoveryClient:
    def __init__(self, client: Client, prefix: str = None):
        self.client = client
        if prefix:
            if prefix.endswith("/"):
                prefix = prefix[:-1]
            if not prefix.startswith("/"):
                prefix = f"/{prefix}"
        self.prefix = prefix

    def get(
        self, proposal_id: typing.Union[str, UUID], discovery_id: typing.Any
    ) -> schemas.DataDiscovery:
        response = self.client.get(
            f"{self.prefix}/{proposal_id}/discoveries/{discovery_id}"
        )
        response.raise_for_status()
        return schemas.DataDiscovery(**response.json())

    def get_multi(
        self, proposal_id: typing.Union[str, UUID], skip: int = 0, limit: int = 100
    ) -> typing.List[schemas.DataDiscovery]:
        response = self.client.get(
            f"{self.prefix}/{proposal_id}/discoveries",
            params={"skip": skip, "limit": limit},
        )
        response.raise_for_status()
        return [schemas.DataDiscovery(**item) for item in response.json()]

    def create(
        self,
        proposal_id: typing.Union[str, UUID],
        resource: schemas.DataDiscoveryCreate,
    ) -> schemas.DataDiscovery:
        response = self.client.post(
            f"{self.prefix}/{proposal_id}/discoveries", json=jsonable_encoder(resource)
        )
        response.raise_for_status()
        return schemas.DataDiscovery(**response.json())

    def update(
        self,
        proposal_id: typing.Union[str, UUID],
        discovery_id: typing.Any,
        resource: schemas.DataDiscoveryUpdate,
    ) -> schemas.DataDiscovery:
        response = self.client.put(
            f"{self.prefix}/{proposal_id}/discoveries/{discovery_id}",
            json=jsonable_encoder(resource.dict(exclude_none=True, exclude_unset=True)),
        )
        response.raise_for_status()
        return schemas.DataDiscovery(**response.json())

    def delete(
        self, proposal_id: typing.Union[str, UUID], discovery_id: typing.Any
    ) -> schemas.DataDiscovery:
        response = self.client.delete(
            f"{self.prefix}/{proposal_id}/discoveries/{discovery_id}"
        )
        response.raise_for_status()
        return schemas.DataDiscovery(**response.json())

    def submit_discovery_statistics(
        self,
        proposal_id: typing.Union[str, UUID],
        discovery_id: typing.Any,
        statistics: StatisticsCreate,
    ) -> DiscoveryStatistics:
        response = self.client.post(
            f"{self.prefix}/{proposal_id}/discoveries/{discovery_id}/stats",
            json=jsonable_encoder(statistics),
        )
        response.raise_for_status()
        return DiscoveryStatistics(**response.json())

    def get_aggregated_results(
        self,
        proposal_id: typing.Union[str, UUID],
        discovery_id: typing.Any,
        features: typing.Union[typing.List[str], str] = None,
    ) -> schemas.DiscoverySummary:

        if features:
            if isinstance(features, str):
                features = [features]
            features = ",".join(features)

        response = self.client.get(
            f"{self.prefix}/{proposal_id}/discoveries/{discovery_id}/summary",
            params={"features": features} if features else None,
        )
        response.raise_for_status()
        return schemas.DiscoverySummary(**response.json())

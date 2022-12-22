import typing

from fastapi.encoders import jsonable_encoder
from httpx import Client
from pydantic import BaseModel

ResourceSchema = typing.TypeVar("ResourceSchema", bound=BaseModel)
CreateSchemaType = typing.TypeVar("CreateSchemaType", bound=BaseModel)
UpdateSchemaType = typing.TypeVar("UpdateSchemaType", bound=BaseModel)


class ResourceClient(
    typing.Generic[ResourceSchema, CreateSchemaType, UpdateSchemaType]
):
    def __init__(
        self, client: Client, schema: typing.Type[ResourceSchema], prefix: str = None
    ):
        """
        A client for a resource from the aggregator API defined as a pydantic model.
        Args:
            client: httpx client to perform requests, expected to be a Client from pht_federated.client.federated_client
                but any httpx client configured with a base_url should work
            schema: the main pydantic model for the resource
            prefix: optional prefix for the resource
        """
        self.client = client
        if prefix:
            if prefix.endswith("/"):
                prefix = prefix[:-1]
            if not prefix.startswith("/"):
                prefix = f"/{prefix}"
        self.prefix = prefix
        self.schema = schema

    def get(self, resource_id: typing.Any) -> ResourceSchema:
        """
        Get a single resource by its id
        Args:
            resource_id:

        Returns:
            The resource parsed as a pydantic model

        Raises:
            httpx.HTTPError: If the request fails
        """
        response = self.client.get(f"{self.prefix}/{resource_id}")
        response.raise_for_status()
        return self.schema(**response.json())

    def get_multi(self, skip: int = 0, limit: int = 100) -> typing.List[ResourceSchema]:
        """
        Get a list of resources with pagination
        Args:
            skip: where to start in the list
            limit: until how many resources to return

        Returns:
            A list of resources parsed as pydantic models
        Raises:
            httpx.HTTPError: If the request fails
        """
        response = self.client.get(
            f"{self.prefix}", params={"skip": skip, "limit": limit}
        )
        response.raise_for_status()
        return [self.schema(**item) for item in response.json()]

    def create(self, resource: CreateSchemaType) -> ResourceSchema:
        """
        Create a new resource on the aggregator
        Args:
            resource: instance of a pydantic model following the schema defined for the creation of the resource

        Returns:
            The created resource parsed as a pydantic model

        Raises:
            httpx.HTTPError: If the request fails
        """
        response = self.client.post(f"{self.prefix}", json=jsonable_encoder(resource))
        response.raise_for_status()
        return self.schema(**response.json())

    def update(
        self, resource_id: typing.Any, resource: UpdateSchemaType
    ) -> ResourceSchema:
        """
        Update a resource on the aggregator

        Args:
            resource_id: the id of the resource
            resource: a pydantic model following the schema defined for the update of the resource

        Returns:
            The updated resource parsed as a pydantic model

        Raises:
            httpx.HTTPError: If the request fails
        """

        response = self.client.put(
            f"{self.prefix}/{resource_id}",
            json=jsonable_encoder(resource.dict(exclude_none=True)),
        )
        response.raise_for_status()
        return self.schema(**response.json())

    def delete(self, resource_id: typing.Any) -> ResourceSchema:
        """
        Delete a resource on the aggregator
        Args:
            resource_id: the id of the resource

        Returns:
            The deleted resource parsed as a pydantic model

        Raises:
            httpx.HTTPError: If the request fails
        """
        response = self.client.delete(f"{self.prefix}/{resource_id}")
        response.raise_for_status()
        return self.schema(**response.json())

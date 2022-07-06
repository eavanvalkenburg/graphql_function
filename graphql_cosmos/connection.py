"""Code to setup connection to CosmosDB."""
from __future__ import annotations

import functools
import os
from collections.abc import Awaitable
from dataclasses import dataclass
from typing import Any

from azure.cosmos.aio import ContainerProxy, CosmosClient, DatabaseProxy


@dataclass
class CosmosInfo:
    """Information about the CosmosDB connection."""

    client: CosmosClient
    database: DatabaseProxy
    container: ContainerProxy
    partition_key: str
    costs: float = 0.0

    @classmethod
    def from_env(cls):
        """Get CosmosInfo from environment variables."""
        return cls(
            *get_cosmos_client(),
            os.environ["CosmosPartitionKey"],
        )

    def reset_costs(self) -> None:
        """Reset the costs."""
        self.costs = 0.0

    def update_costs(  # pylint: disable=no-self-argument
        func: Awaitable[Any],
    ) -> Awaitable[Any]:
        """Decorate the function with the costs."""

        @functools.wraps(func)
        async def wrapper(self: "CosmosInfo", *args, **kwargs):
            """Wrapper for the function."""
            value = await func(self, *args, **kwargs)  # pylint: disable=not-callable
            self.costs += float(
                self.client.client_connection.last_response_headers[
                    "x-ms-request-charge"
                ]
            )
            return value

        return wrapper

    @update_costs
    async def query(self, **kwargs: Any) -> list[dict[str, Any]] | None:
        """Run a query against Cosmos."""
        item_id = kwargs.get("id")
        address = kwargs.get("address")
        
        if item_id and address:
            return [await self.container.read_item(item=item_id, partition_key=address)]
        
        if not item_id and not address:
            return [item async for item in self.container.read_all_items()]
        
        params = {
            "query": "SELECT * FROM c WHERE c.id = @id OR c.address = @address",
            "parameters": [
                {"name": "@id", "value": item_id},
                {"name": "@address", "value": address},
            ],
            "populate_query_metrics": True,
        }
        if address:
            params["partition_key"] = address
        return [item async for item in self.container.query_items(**params)]


def get_cosmos_client() -> tuple[CosmosClient, DatabaseProxy, ContainerProxy]:
    """Get a CosmosClient connected to the right DB and container."""
    cosmos_url = os.environ["CosmosURL"]
    cosmos_key = os.environ["CosmosKey"]
    cosmos_db = os.environ["CosmosDatabase"]
    cosmos_container = os.environ["CosmosContainer"]

    client = CosmosClient(cosmos_url, credential=cosmos_key)
    database = client.get_database_client(cosmos_db)
    container = database.get_container_client(cosmos_container)
    return client, database, container

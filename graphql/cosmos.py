"""Code to setup connection to CosmosDB."""
from __future__ import annotations

import functools
import os
from collections.abc import Awaitable
from dataclasses import dataclass
from typing import Any
from uuid import uuid4

from azure.cosmos.aio import ContainerProxy, CosmosClient, DatabaseProxy

from .const import (
    ENV_COSMOS_CONTAINER_FIELD,
    ENV_COSMOS_DATABASE_FIELD,
    ENV_COSMOS_KEY_FIELD,
    ENV_COSMOS_PARTITION_KEY_FIELD,
    ENV_COSMOS_URL_FIELD,
)


@dataclass
class CosmosInfo:
    """Information about the CosmosDB connection."""

    client: CosmosClient
    database: DatabaseProxy
    container: ContainerProxy
    partition_key_field: str
    costs: float = 0.0

    @classmethod
    def from_env(cls):
        """Get CosmosInfo from environment variables."""
        client = CosmosClient(
            os.environ[ENV_COSMOS_URL_FIELD],
            credential=os.environ[ENV_COSMOS_KEY_FIELD],
        )
        database = client.get_database_client(os.environ[ENV_COSMOS_DATABASE_FIELD])
        container = database.get_container_client(
            os.environ[ENV_COSMOS_CONTAINER_FIELD]
        )

        return cls(
            client,
            database,
            container,
            os.environ[ENV_COSMOS_PARTITION_KEY_FIELD],
        )

    def reset_costs(self) -> None:
        """Reset the costs."""
        self.costs = 0.0

    def update_costs(  # pylint: disable=no-self-argument
        func: Awaitable[Any],
    ) -> Awaitable[Any]:
        """Decorate functions with this to store the costs."""

        @functools.wraps(func)
        async def wrapper(self: "CosmosInfo", *args, **kwargs):
            """Wrapper for the function."""
            value = await func(self, *args, **kwargs)  # pylint: disable=not-callable
            if self.client.client_connection.last_response_headers:
                self.costs += float(
                    self.client.client_connection.last_response_headers[
                        "x-ms-request-charge"
                    ]
                )
            return value

        return wrapper

    # From this function onwards the specifics of your documents need to be implemented.
    @update_costs
    async def query(self, **kwargs: Any) -> list[dict[str, Any]] | None:
        """Run a query against Cosmos."""
        item_id = kwargs.get("id")
        address = kwargs.get("address")
        partition_key = kwargs.get(self.partition_key_field)

        if item_id and partition_key:
            return [
                await self.container.read_item(
                    item=item_id, partition_key=partition_key
                )
            ]

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
        if partition_key:
            params["partition_key"] = partition_key
        return [item async for item in self.container.query_items(**params)]

    @update_costs
    async def upsert(self, **kwargs: Any) -> dict[str, Any]:
        """Upsert an item in Cosmos."""
        new_item = kwargs.get("input")
        if not new_item:
            return {"status": False, "error": "No input provided for upsert."}

        partition_key = new_item.get(self.partition_key_field)
        if not partition_key:
            return {
                "status": False,
                "error": f"Partition key ({self.partition_key_field}) is required.",
            }

        if "address" not in new_item:
            return {"status": False, "error": "Address is required."}
        if "id" not in new_item:
            new_item["id"] = str(uuid4())

        await self.container.upsert_item(new_item, partition_key=partition_key)
        return {
            "status": True,
            "error": None,
            "partition_key": partition_key,
            "id": new_item["id"],
            "address": new_item["address"],
        }


# Load the CosmosDB Connection from environment variables
cosmos = CosmosInfo.from_env()
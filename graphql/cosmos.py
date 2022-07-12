"""Code to setup connection to CosmosDB."""
from __future__ import annotations

import logging
import functools
from collections.abc import Awaitable
from dataclasses import dataclass
from typing import Any
from uuid import uuid4

from azure.cosmos.aio import ContainerProxy, CosmosClient, DatabaseProxy

from .const import (
    ENV_COSMOS_DATABASE,
    ENV_COSMOS_KEY,
    ENV_COSMOS_URL,
    ENV_COSMOS_CONTAINER,
    ENV_COSMOS_PARTITION_KEY,
)

_LOGGER = logging.getLogger(__name__)


@dataclass
class CosmosInfo:
    """Information about the CosmosDB connection."""

    client: CosmosClient
    database: DatabaseProxy
    container: ContainerProxy
    partition_key_field: str
    last_response_headers: dict[str, str] = None

    @classmethod
    def from_env(cls):
        """Get CosmosInfo from environment variables."""
        client = CosmosClient(ENV_COSMOS_URL, credential=ENV_COSMOS_KEY)
        database = client.get_database_client(ENV_COSMOS_DATABASE)
        container = database.get_container_client(ENV_COSMOS_CONTAINER)

        return cls(
            client,
            database,
            container,
            ENV_COSMOS_PARTITION_KEY,
        )

    @property
    def costs(self) -> float:
        """Get the costs."""
        if (
            self.last_response_headers
            and "x-ms-request-charge" in self.last_response_headers
        ):
            return float(self.last_response_headers["x-ms-request-charge"])
        return 0.0

    @property
    def session_token(self) -> str | None:
        """Get the session token."""
        if (
            self.last_response_headers
            and "x-ms-session-token" in self.last_response_headers
        ):
            return self.last_response_headers["x-ms-session-token"]
        return None

    @property
    def continuation(self) -> str | None:
        """Get the session token."""
        if (
            self.last_response_headers
            and "x-ms-continuation" in self.last_response_headers
        ):
            return self.last_response_headers["x-ms-continuation"]
        return None

    def update_last_response(
        self, last_response_headers: dict[str, str], *_: dict[str, Any]
    ) -> None:
        """Hook to update the last response."""
        self.last_response_headers = last_response_headers

    # From this function onwards the specifics of your documents need to be implemented.
    async def query(self, **kwargs: Any) -> list[dict[str, Any]] | None:
        """Run a query against Cosmos."""
        item_id = kwargs.get("id")
        address = kwargs.get("address")
        max_item_count = kwargs.get("max_item_count")
        partition_key = kwargs.get(self.partition_key_field)

        if item_id and partition_key:
            return [
                await self.container.read_item(
                    item=item_id,
                    partition_key=partition_key,
                    session_token=self.session_token,
                )
            ]

        if not item_id and not address:
            resp = self.container.read_all_items(
                max_item_count=max_item_count,
                session_token=self.session_token,
                response_hook=self.update_last_response,
                continuation=self.continuation,
            )
            first_page = await resp.by_page().__anext__()
            return [item async for item in first_page]

        params = {
            "query": "SELECT * FROM c WHERE c.id = @id OR c.address = @address",
            "parameters": [
                {"name": "@id", "value": item_id},
                {"name": "@address", "value": address},
            ],
            "populate_query_metrics": True,
            "max_item_count": max_item_count,
            "session_token": self.session_token,
            "enable_cross_partition_query": False,
            "response_hook": self.update_last_response,
            "continuation": self.continuation,
        }
        if partition_key:
            params["partition_key"] = partition_key
        resp = self.container.query_items(**params)
        first_page = await resp.by_page().__anext__()
        return [item async for item in first_page]

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

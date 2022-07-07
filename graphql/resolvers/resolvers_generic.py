"""Generic resolvers specific to Cosmos."""
from __future__ import annotations

from datetime import datetime
from typing import Any

from ariadne.types import GraphQLResolveInfo

from ..const import COSMOS_FIELD_TS
from ..cosmos import cosmos


async def resolve_cosmos_query(
    obj: Any,  # pylint: disable=unused-argument
    info: GraphQLResolveInfo,  # pylint: disable=unused-argument
    **kwargs: Any,
) -> list[dict[str, Any]]:
    """Resolve the container query."""
    return await cosmos.query(**kwargs)


async def resolve_cosmos_mutation(
    obj: Any,  # pylint: disable=unused-argument
    info: GraphQLResolveInfo,  # pylint: disable=unused-argument
    **kwargs: Any,
) -> list[dict[str, Any]]:
    """Resolve the container query."""
    return await cosmos.upsert(**kwargs)


async def resolve_timestamp(
    obj: dict[str, Any], info: GraphQLResolveInfo  # pylint: disable=unused-argument
) -> Any:
    """Sample resolver that turns the Unix Timestamp into a iso-formatted timestamp."""
    return datetime.fromtimestamp(obj[COSMOS_FIELD_TS]).isoformat()


async def resolve_partition_key(
    obj: dict[str, Any], info: GraphQLResolveInfo  # pylint: disable=unused-argument
) -> Any:
    """Sample resolver that returns the value of the partition_key field."""
    return obj[cosmos.partition_key_field]


async def resolve_costs(
    obj: Any, info: GraphQLResolveInfo  # pylint: disable=unused-argument
) -> int:
    """Resolve the costs field."""
    return cosmos.costs

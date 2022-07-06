"""All the resolvers for the queries and mutations."""
from __future__ import annotations

import logging
from typing import Any

from ariadne import ObjectType, load_schema_from_path, make_executable_schema
from ariadne.types import GraphQLResolveInfo

from .connection import CosmosInfo

_LOGGER = logging.getLogger(__name__)

cosmos = CosmosInfo.from_env()

# Schema doc: https://graphql.org/learn/schema/
type_defs = load_schema_from_path("./graphql_cosmos/schemas")

query = ObjectType("Query")
container = ObjectType("Container")


@query.field("hello")
async def resolve_hello(
    obj: Any, info: GraphQLResolveInfo
) -> str:  # pylint: disable=unused-argument
    """Resolve the hello query."""
    return f"Hello, {info.context.headers.get('User-Agent', 'Guest')}!"


@query.field("costs")
async def resolve_cost(
    obj: Any, info: GraphQLResolveInfo
) -> int:  # pylint: disable=unused-argument
    """Resolve the hello query."""
    return cosmos.costs


@query.field("container")
async def resolve_container(
    obj: Any,  # pylint: disable=unused-argument
    info: GraphQLResolveInfo,  # pylint: disable=unused-argument
    **kwargs: Any,
) -> list[dict[str, Any]]:
    """Resolve the container query."""
    return await cosmos.query(**kwargs)


schema = make_executable_schema(type_defs, query, container)

# Sample resolver if needed to manipulate the returned data from Cosmos.
# @sample.field("id")
# async def resolve_id(obj: dict[str, Any], info: GraphQLResolveInfo) -> Any:
#     """Sample resolver if necessary."""
#     return obj["id"]

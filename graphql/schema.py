"""All the resolvers for the queries and mutations."""
from __future__ import annotations

import json

from ariadne import (
    MutationType,
    ObjectType,
    QueryType,
    graphql,
    load_schema_from_path,
    make_executable_schema,
)
from azure.functions import HttpRequest

from .const import (
    CONTAINER_NAME,
    COSMOS_FIELD_CONTINUATION,
    COSMOS_FIELD_COSTS,
    COSMOS_FIELD_PARTITION_KEY,
    COSMOS_FIELD_PARTITION_KEY_FIELD,
    COSMOS_FIELD_TIMESTAMP,
)
from .cosmos import cosmos
from .resolvers import (  # resolve_timestamp_timezone,
    resolve_continuation,
    resolve_cosmos_mutation,
    resolve_cosmos_query,
    resolve_costs,
    resolve_partition_key,
    resolve_partition_key_field,
    resolve_timestamp,
)

# Load the schemas
type_defs = load_schema_from_path("./schemas")

# Define the outside types, not defined is Introspection
query = QueryType()
query.set_field("container", resolve_cosmos_query)
query.set_field(COSMOS_FIELD_COSTS, resolve_costs)
query.set_field(COSMOS_FIELD_CONTINUATION, resolve_continuation)

mutation = MutationType()
mutation.set_field("container", resolve_cosmos_mutation)
mutation.set_field(COSMOS_FIELD_COSTS, resolve_costs)

# Define the actual objects in CosmosDB
container = ObjectType(CONTAINER_NAME)
container.set_field(COSMOS_FIELD_PARTITION_KEY, resolve_partition_key)
container.set_field(COSMOS_FIELD_PARTITION_KEY_FIELD, resolve_partition_key_field)
container.set_field(COSMOS_FIELD_TIMESTAMP, resolve_timestamp)
# container.set_field(COSMOS_FIELD_TIMESTAMP, resolve_timestamp_timezone)

schema = make_executable_schema(type_defs, query, container, mutation)


async def parse_query(func_req: HttpRequest) -> tuple[str, int]:
    """Wrap the graphql function."""
    success, result = await graphql(schema, func_req.get_json(), context_value=func_req)
    if COSMOS_FIELD_COSTS in result["data"]:
        result["data"][COSMOS_FIELD_COSTS] = cosmos.costs
    if COSMOS_FIELD_CONTINUATION in result["data"]:
        result["data"][COSMOS_FIELD_CONTINUATION] = cosmos.continuation
    return json.dumps(result), (200 if success else 400)

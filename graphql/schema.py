"""All the resolvers for the queries and mutations."""
from __future__ import annotations

import json
from azure.functions import HttpRequest
from ariadne import (
    graphql,
    MutationType,
    ObjectType,
    QueryType,
    load_schema_from_path,
    make_executable_schema,
)

from .const import (
    COSMOS_FIELD_COSTS,
    COSMOS_FIELD_PARTITION_KEY,
    COSMOS_FIELD_PARTITION_KEY_FIELD,
    COSMOS_FIELD_TIMESTAMP,
    CONTAINER_NAME,
)
from .resolvers import (
    resolve_cosmos_mutation,
    resolve_cosmos_query,
    resolve_costs,
    resolve_partition_key,
    resolve_timestamp,
    resolve_partition_key_field,
    # resolve_timestamp_timezone,
)
from .cosmos import cosmos


# Load the schemas
type_defs = load_schema_from_path("./schemas")

# Define the outside types, not defined is Introspection
query = QueryType()
query.set_field("container", resolve_cosmos_query)
query.set_field(COSMOS_FIELD_COSTS, resolve_costs)

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
    cosmos.reset_costs()
    success, result = await graphql(schema, func_req.get_json(), context_value=func_req)
    if COSMOS_FIELD_COSTS in result["data"]:
        result["data"][COSMOS_FIELD_COSTS] = cosmos.costs
    return json.dumps(result), (200 if success else 400)

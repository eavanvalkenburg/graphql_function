"""All the resolvers for the queries and mutations."""
import json
from azure.functions import HttpRequest
from ariadne import (
    ObjectType,
    graphql,
    make_executable_schema,
    load_schema_from_path,
)

type_defs = load_schema_from_path("./graphql_cosmos/schemas")

query = ObjectType("Query")
user = ObjectType("User")


@query.field("hello")
async def resolve_hello(_, info):
    """Resolve the hello query."""
    request = info.context
    user_agent = request.headers.get("User-Agent", "Guest")
    return f"Hello, {user_agent}!"


@query.field("user")
async def resolve_user(_, info):
    return info


@user.field("username")
async def resolve_username(obj, *_):
    return obj.context.headers.get("User-Agent")


schema = make_executable_schema(type_defs, query, user)


async def parse_query(func_req: HttpRequest) -> tuple[str, int]:
    """Wrap the function of Ariadne."""
    success, result = await graphql(schema, func_req.get_json(), context_value=func_req)
    return json.dumps(result), (200 if success else 400)

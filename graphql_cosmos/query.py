"""All the resolvers for the queries and mutations."""
import json
import logging

from ariadne import graphql
from azure.functions import HttpRequest

from .schema import cosmos, schema

_LOGGER = logging.getLogger(__name__)


async def parse_query(func_req: HttpRequest) -> tuple[str, int]:
    """Wrap the function of Ariadne."""
    cosmos.reset_costs()
    success, result = await graphql(schema, func_req.get_json(), context_value=func_req)
    if "costs" in result["data"]:
        result["data"]["costs"] = cosmos.costs
    return json.dumps(result), (200 if success else 400)

import logging

import azure.functions as func
from ariadne import QueryType, graphql_sync, make_executable_schema
from ariadne.constants import PLAYGROUND_HTML

type_defs = """
    type Query {
        hello: String!
    }
"""

query = QueryType()


@query.field("hello")
def resolve_hello(_, info):
    request = info.context
    user_agent = request.headers.get("User-Agent", "Guest")
    return "Hello, %s!" % user_agent


schema = make_executable_schema(type_defs, query)


def main(graphql: func.HttpRequest) -> func.HttpResponse:
    logging.info("Python HTTP trigger function processed a request.")

    verb = graphql.method.upper()

    if verb == "GET":
        return func.HttpResponse(
            PLAYGROUND_HTML,
            mimetype="text/html",
            status_code=200,
        )
    if verb == "POST":
        data = graphql.get_json()
        success, result = graphql_sync(schema, data, context_value=graphql)
        return func.HttpResponse(result, 200 if success else 400)

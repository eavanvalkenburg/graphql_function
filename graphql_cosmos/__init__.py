"""Main azure function, calls the resolvers for the ariadne sync wrapper."""
import logging

import azure.functions as func
from azure.functions import HttpRequest, HttpResponse
from ariadne.constants import PLAYGROUND_HTML
from .resolvers import parse_query


async def main(graphql: HttpRequest) -> HttpResponse:
    """Main function called by Azure Functions."""
    if graphql.method == "GET":
        return HttpResponse(
            PLAYGROUND_HTML,
            mimetype="text/html",
            status_code=200,
        )
    if graphql.method == "POST":
        result, status_code = await parse_query(graphql)
        logging.info("result was %s", result)
        logging.info("status was %s", status_code)
        return HttpResponse(
            result, mimetype="application/json", status_code=status_code
        )

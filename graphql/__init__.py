"""Main azure function, calls the resolvers for the ariadne sync wrapper."""
import logging

from ariadne.constants import DATA_TYPE_JSON, PLAYGROUND_HTML
from azure.functions import HttpRequest, HttpResponse

from .const import MIME_TYPE_TEXT_HTML
from .schema import parse_query


async def main(graphql: HttpRequest) -> HttpResponse:
    """Main function called by Azure Functions."""
    if graphql.method == "GET":
        return HttpResponse(
            PLAYGROUND_HTML,
            status_code=200,
            mimetype=MIME_TYPE_TEXT_HTML,
        )
    if graphql.method == "POST":
        result, status_code = await parse_query(graphql)
        logging.debug("Status was %s", status_code)
        logging.debug("Result was %s", result)
        return HttpResponse(
            result,
            status_code=status_code,
            mimetype=DATA_TYPE_JSON,
        )

"""Constants for GraphQL."""
from typing import Final
import os


MIME_TYPE_TEXT_HTML: Final = "text/html"

MUTATION_NAME: Final = "Mutation"
QUERY_NAME: Final = "Query"
CONTAINER_NAME: Final = "Container"

COSMOS_FIELD_COSTS: Final = "costs"
COSMOS_FIELD_ID: Final = "id"
COSMOS_FIELD_PARTITION_KEY: Final = "partition_key"
COSMOS_FIELD_PARTITION_KEY_FIELD: Final = "partition_key_field"
COSMOS_FIELD_RID: Final = "_rid"
COSMOS_FIELD_SELF: Final = "_self"
COSMOS_FIELD_ETAG: Final = "_etag"
COSMOS_FIELD_TS: Final = "_ts"
COSMOS_FIELD_ATTACHMENT: Final = "_attachments"
COSMOS_FIELD_TIMESTAMP: Final = "timestamp"

ENV_COSMOS_URL = os.environ.get("CosmosURL")
ENV_COSMOS_KEY = os.environ.get("CosmosKey")
ENV_COSMOS_DATABASE = os.environ.get("CosmosDatabase")
ENV_COSMOS_CONTAINER = os.environ.get("CosmosContainer")
ENV_COSMOS_PARTITION_KEY = os.environ.get("CosmosPartitionKey")

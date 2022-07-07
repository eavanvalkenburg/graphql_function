"""All the resolvers for the queries and mutations."""
from __future__ import annotations

import logging
from datetime import datetime, timezone
from typing import Any

from ariadne.types import GraphQLResolveInfo

from ..const import COSMOS_FIELD_TS

_LOGGER = logging.getLogger(__name__)


async def resolve_timestamp_timezone(
    obj: dict[str, Any], info: GraphQLResolveInfo  # pylint: disable=unused-argument
) -> Any:
    """Sample resolver that turns the Unix Timestamp into a iso-formatted timestamp with timezone.

    Meant as a drop-in replacement for the built-in `resolve_timestamp` resolver.
    """
    date_time = datetime.fromtimestamp(obj[COSMOS_FIELD_TS])
    date_time.astimezone(timezone.utc)
    return date_time.isoformat()

"""All the resolvers for the queries and mutations."""
from __future__ import annotations

import logging
from datetime import datetime
from typing import Any
from pytz import timezone, utc

from ariadne.types import GraphQLResolveInfo

from ..const import COSMOS_FIELD_TS

_LOGGER = logging.getLogger(__name__)

LOCAL_TZ = timezone("Europe/Amsterdam")


async def resolve_timestamp_timezone(
    obj: dict[str, Any], info: GraphQLResolveInfo  # pylint: disable=unused-argument
) -> Any:
    """Sample resolver that turns the Unix Timestamp into a iso-formatted timestamp with the timezone defined above.

    Meant as a drop-in replacement for the built-in `resolve_timestamp` resolver.
    """
    return (
        datetime.fromtimestamp(obj[COSMOS_FIELD_TS], tz=utc)
        .astimezone(LOCAL_TZ)
        .isoformat()
    )

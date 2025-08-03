from typing import Any, Optional

from .json_utils import parse_json
from .protocols import BaseRequestProtocol
from .request._base import QueryParams


def is_request_allowed(
    request: BaseRequestProtocol, allowed_methods: tuple[str, ...] = ("GET", "POST")
) -> bool:
    """Check if the request method is allowed."""
    return request.method in allowed_methods


def should_render_ide(
    request: BaseRequestProtocol,
    check_query_param: Optional[str] = "query",
    supported_headers: tuple[str, ...] = ("text/html", "*/*"),
) -> bool:
    """Check if an IDE should be rendered based on request parameters.

    Returns True if:
    - Method is GET
    - No query parameter is present (or the specified param is None)
    - Accept header contains one of the supported types
    """
    if request.method != "GET":
        return False

    if check_query_param and request.query_params.get(check_query_param) is not None:
        return False

    accept_header = request.headers.get("accept", "")
    return any(
        supported_header in accept_header for supported_header in supported_headers
    )


def parse_query_params(
    params: QueryParams, json_fields: tuple[str, ...] = ("variables", "extensions")
) -> dict[str, Any]:
    """Parse query parameters, decoding JSON fields as needed.

    Args:
        params: The query parameters to parse
        json_fields: Field names that should be JSON-decoded

    Returns:
        Dictionary with parsed parameters
    """
    result = dict(params)

    for field in json_fields:
        if field in result:
            value = result[field]
            if value:
                result[field] = parse_json(value)

    return result


__all__ = ["is_request_allowed", "should_render_ide", "parse_query_params"]

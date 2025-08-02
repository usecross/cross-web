import json
from typing import Any, Union

from .exceptions import HTTPException


def parse_json(data: Union[str, bytes]) -> Any:
    """Parse JSON data with proper error handling for HTTP responses."""
    try:
        return json.loads(data)
    except json.JSONDecodeError as e:
        raise HTTPException(400, "Unable to parse request body as JSON") from e


def decode_json(data: Union[str, bytes]) -> Any:
    """Decode JSON data from string or bytes."""
    return json.loads(data)


def encode_json(data: Any) -> str:
    """Encode data as JSON string."""
    return json.dumps(data)


__all__ = ["parse_json", "decode_json", "encode_json"]
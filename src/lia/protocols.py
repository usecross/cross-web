from collections.abc import Mapping
from typing import Optional, Protocol, Union

from .request._base import HTTPMethod


class BaseRequestProtocol(Protocol):
    """Protocol defining the minimal interface for HTTP requests."""

    @property
    def query_params(self) -> Mapping[str, Optional[Union[str, list[str]]]]: ...

    @property
    def method(self) -> HTTPMethod: ...

    @property
    def headers(self) -> Mapping[str, str]: ...


__all__ = ["BaseRequestProtocol"]

import abc
from collections.abc import Mapping
from dataclasses import dataclass
from typing import Any, Literal, Optional, Union

HTTPMethod = Literal[
    "GET", "POST", "PUT", "DELETE", "PATCH", "HEAD", "OPTIONS", "TRACE"
]

QueryParams = Mapping[str, Optional[str]]


@dataclass
class FormData:
    files: Mapping[str, Any]
    form: Mapping[str, Any]

    def get(self, key: str) -> Any:
        return self.form.get(key)


class SyncHTTPRequestAdapter(abc.ABC):
    """
    Abstract Base Class defining the interface for accessing HTTP request data
    in a framework-agnostic way for synchronous operations.
    """

    @property
    @abc.abstractmethod
    def method(self) -> HTTPMethod:
        """The HTTP method of the request (e.g., 'GET', 'POST')."""
        raise NotImplementedError

    @property
    @abc.abstractmethod
    def query_params(self) -> QueryParams:
        """The query parameters of the request."""
        raise NotImplementedError

    @property
    @abc.abstractmethod
    def headers(self) -> Mapping[str, str]:
        """The request headers. Header names should ideally be case-insensitive."""
        # Note: Real implementations might need to handle case-insensitivity
        raise NotImplementedError

    @property
    @abc.abstractmethod
    def content_type(self) -> Optional[str]:
        """The 'Content-Type' header value, if present."""
        raise NotImplementedError

    @property
    @abc.abstractmethod
    def body(self) -> Union[str, bytes]:
        """Return the raw request body as bytes or string."""
        raise NotImplementedError

    @property
    @abc.abstractmethod
    def post_data(self) -> Mapping[str, Union[str, bytes]]:
        """Return the parsed POST data as a mapping of field names to values."""
        raise NotImplementedError

    @property
    @abc.abstractmethod
    def files(self) -> Mapping[str, Any]:
        """Return uploaded files from the request."""
        raise NotImplementedError

    @abc.abstractmethod
    def get_form_data(self) -> FormData:
        """
        Return parsed form data (multipart/form-data or application/x-www-form-urlencoded).
        Returns an empty FormData object if the content type is not form data
        or if parsing fails.
        """
        raise NotImplementedError

    @property
    @abc.abstractmethod
    def url(self) -> str:
        """The URL of the request."""
        raise NotImplementedError

    @property
    @abc.abstractmethod
    def cookies(self) -> Mapping[str, str]:
        """The request cookies."""
        raise NotImplementedError


class AsyncHTTPRequestAdapter(abc.ABC):
    """
    Abstract Base Class defining the interface for accessing HTTP request data
    in a framework-agnostic way.
    """

    @property
    @abc.abstractmethod
    def method(self) -> HTTPMethod:
        """The HTTP method of the request (e.g., 'GET', 'POST')."""
        raise NotImplementedError

    @property
    @abc.abstractmethod
    def query_params(self) -> QueryParams:
        """The query parameters of the request."""
        raise NotImplementedError

    @property
    @abc.abstractmethod
    def headers(self) -> Mapping[str, str]:
        """The request headers. Header names should ideally be case-insensitive."""
        # Note: Real implementations might need to handle case-insensitivity
        raise NotImplementedError

    @property
    @abc.abstractmethod
    def content_type(self) -> Optional[str]:
        """The 'Content-Type' header value, if present."""
        raise NotImplementedError

    @abc.abstractmethod
    async def get_body(self) -> bytes:
        """Return the raw request body as bytes."""
        raise NotImplementedError

    @abc.abstractmethod
    async def get_form_data(self) -> FormData:
        """
        Return parsed form data (multipart/form-data or application/x-www-form-urlencoded).
        Returns an empty FormData object if the content type is not form data
        or if parsing fails.
        """
        raise NotImplementedError

    @property
    @abc.abstractmethod
    def url(self) -> str:
        """The URL of the request."""
        raise NotImplementedError

    @property
    @abc.abstractmethod
    def cookies(self) -> Mapping[str, str]:
        """The request cookies."""
        raise NotImplementedError

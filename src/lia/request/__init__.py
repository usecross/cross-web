from __future__ import annotations

from typing import TYPE_CHECKING, Mapping, Optional, Any

from typing_extensions import Self

if TYPE_CHECKING:
    from starlette.requests import Request as StarletteRequest

from ._base import AsyncHTTPRequestAdapter, FormData, HTTPMethod, QueryParams
from ._starlette import StarletteRequestAdapter
from ._testing import TestingRequestAdapter


class AsyncHTTPRequest:
    def __init__(self, adapter: AsyncHTTPRequestAdapter) -> None:
        self._adapter = adapter

    @classmethod
    def from_starlette(cls, request: StarletteRequest) -> Self:
        adapter = StarletteRequestAdapter(request)

        return cls(adapter)

    @classmethod
    def from_fastapi(cls, request: StarletteRequest) -> Self:
        return cls.from_starlette(request)

    @classmethod
    def from_django(cls, request: Any) -> Self:
        # Import here to avoid circular imports and optional Django dependency
        from ._django import AsyncDjangoHTTPRequestAdapter

        adapter = AsyncDjangoHTTPRequestAdapter(request)
        return cls(adapter)

    @classmethod
    def from_flask(cls, request: Any) -> Self:
        # Import here to avoid circular imports and optional Flask dependency
        from ._flask import AsyncFlaskHTTPRequestAdapter

        adapter = AsyncFlaskHTTPRequestAdapter(request)
        return cls(adapter)

    @classmethod
    def from_sanic(cls, request: Any) -> Self:
        # Import here to avoid circular imports and optional Sanic dependency
        from ._sanic import SanicHTTPRequestAdapter

        adapter = SanicHTTPRequestAdapter(request)
        return cls(adapter)

    @classmethod
    def from_aiohttp(cls, request: Any) -> Self:
        # Import here to avoid circular imports and optional aiohttp dependency
        from ._aiohttp import AiohttpHTTPRequestAdapter

        adapter = AiohttpHTTPRequestAdapter(request)
        return cls(adapter)

    @classmethod
    def from_quart(cls, request: Any) -> Self:
        # Import here to avoid circular imports and optional Quart dependency
        from ._quart import QuartHTTPRequestAdapter

        adapter = QuartHTTPRequestAdapter(request)
        return cls(adapter)

    @classmethod
    def from_litestar(cls, request: Any) -> Self:
        # Import here to avoid circular imports and optional Litestar dependency
        from ._litestar import LitestarRequestAdapter

        adapter = LitestarRequestAdapter(request)
        return cls(adapter)

    @classmethod
    def from_form_data(cls, data: Mapping[str, str]) -> Self:
        adapter = TestingRequestAdapter(
            form_data=FormData(files={}, form=data),
            content_type="application/x-www-form-urlencoded",
        )
        return cls(adapter)

    @property
    def method(self) -> HTTPMethod:
        """The HTTP method of the request."""
        return self._adapter.method

    @property
    def query_params(self) -> QueryParams:
        """The query parameters of the request."""
        return self._adapter.query_params

    @property
    def headers(self) -> Mapping[str, str]:
        """The request headers (case-insensitive keys recommended)."""
        return self._adapter.headers

    @property
    def content_type(self) -> Optional[str]:
        """The 'Content-Type' header value, if present."""
        return self._adapter.content_type

    @property
    def url(self) -> str:
        """The URL of the request."""
        return self._adapter.url

    @property
    def cookies(self) -> Mapping[str, str]:
        """The request cookies."""
        return self._adapter.cookies

    async def get_body(self) -> bytes:
        """Return the raw request body as bytes."""
        return await self._adapter.get_body()

    async def get_form_data(self) -> FormData:
        """
        Return parsed form data (multipart/form-data or application/x-www-form-urlencoded).
        """
        return await self._adapter.get_form_data()

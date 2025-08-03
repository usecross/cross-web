from __future__ import annotations

from typing import TYPE_CHECKING, Mapping, Optional, cast

from ._base import AsyncHTTPRequestAdapter, FormData, HTTPMethod, QueryParams

if TYPE_CHECKING:
    from starlette.requests import Request


class StarletteRequestAdapter(AsyncHTTPRequestAdapter):
    def __init__(self, request: Request) -> None:
        self._request = request
        # Starlette Headers are case-insensitive Mapping
        self._headers: Optional[Mapping[str, str]] = None

    @property
    def method(self) -> HTTPMethod:
        # Starlette method is already uppercase string
        return cast(HTTPMethod, self._request.method)

    @property
    def query_params(self) -> QueryParams:
        # Starlette QueryParams behaves like a MultiDict Mapping
        return cast(QueryParams, self._request.query_params)

    @property
    def headers(self) -> Mapping[str, str]:
        # Cache the immutable headers object for direct access
        # Starlette Headers are case-insensitive
        if self._headers is None:
            self._headers = self._request.headers

        return self._headers

    @property
    def content_type(self) -> Optional[str]:
        # Access directly via headers property for consistency
        return self.headers.get("content-type")

    async def get_body(self) -> bytes:
        return await self._request.body()

    async def get_form_data(self) -> FormData:
        multipart_data = await self._request.form()

        return FormData(
            files=multipart_data,
            form=multipart_data,
        )

    @property
    def url(self) -> str:
        return str(self._request.url)

    @property
    def cookies(self) -> Mapping[str, str]:
        return cast(Mapping[str, str], self._request.cookies)

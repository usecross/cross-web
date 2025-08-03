from __future__ import annotations

from typing import TYPE_CHECKING, Any, Mapping, Optional, cast

from ._base import AsyncHTTPRequestAdapter, FormData, HTTPMethod, QueryParams

if TYPE_CHECKING:
    from litestar import Request


class LitestarRequestAdapter(AsyncHTTPRequestAdapter):
    def __init__(self, request: Request[Any, Any, Any]) -> None:
        self.request = request

    @property
    def query_params(self) -> QueryParams:
        return self.request.query_params

    @property
    def method(self) -> HTTPMethod:
        return cast("HTTPMethod", self.request.method.upper())

    @property
    def headers(self) -> Mapping[str, str]:
        return self.request.headers

    @property
    def content_type(self) -> Optional[str]:
        content_type, params = self.request.content_type

        # combine content type and params
        if params:
            content_type += "; " + "; ".join(f"{k}={v}" for k, v in params.items())

        return content_type

    async def get_body(self) -> bytes:
        return await self.request.body()

    async def get_form_data(self) -> FormData:
        multipart_data = await self.request.form()

        return FormData(form=multipart_data, files=multipart_data)

    @property
    def url(self) -> str:
        return str(self.request.url)

    @property
    def cookies(self) -> Mapping[str, str]:
        return self.request.cookies

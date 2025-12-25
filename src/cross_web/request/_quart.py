from __future__ import annotations

from typing import TYPE_CHECKING, Mapping, Optional, cast

from ._base import AsyncHTTPRequestAdapter, FormData, HTTPMethod, QueryParams

if TYPE_CHECKING:
    from quart import Request


class QuartHTTPRequestAdapter(AsyncHTTPRequestAdapter):
    def __init__(self, request: Request) -> None:
        self.request = request

    @property
    def query_params(self) -> QueryParams:
        return self.request.args.to_dict()

    @property
    def method(self) -> HTTPMethod:
        return cast("HTTPMethod", self.request.method.upper())

    @property
    def content_type(self) -> Optional[str]:
        return self.request.content_type

    @property
    def headers(self) -> Mapping[str, str]:
        return self.request.headers  # type: ignore

    async def get_body(self) -> bytes:
        return await self.request.data

    async def get_form_data(self) -> FormData:
        files = await self.request.files
        form = await self.request.form
        return FormData(files=files, form=form)

    @property
    def url(self) -> str:
        return self.request.url

    @property
    def cookies(self) -> Mapping[str, str]:
        return self.request.cookies

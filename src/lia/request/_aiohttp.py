from __future__ import annotations

from io import BytesIO
from typing import TYPE_CHECKING, Any, Mapping, Optional, cast

from ._base import AsyncHTTPRequestAdapter, FormData, HTTPMethod, QueryParams

if TYPE_CHECKING:
    from aiohttp import web
    from aiohttp.multipart import BodyPartReader


class AiohttpHTTPRequestAdapter(AsyncHTTPRequestAdapter):
    def __init__(self, request: web.Request) -> None:
        self.request = request

    @property
    def query_params(self) -> QueryParams:
        return self.request.query.copy()  # type: ignore[attr-defined]

    async def get_body(self) -> bytes:
        return await self.request.content.read()

    @property
    def method(self) -> HTTPMethod:
        return cast("HTTPMethod", self.request.method.upper())

    @property
    def headers(self) -> Mapping[str, str]:
        return self.request.headers

    async def get_form_data(self) -> FormData:
        reader = await self.request.multipart()

        data: dict[str, Any] = {}
        files: dict[str, Any] = {}

        while field := await reader.next():
            assert isinstance(field, BodyPartReader)
            assert field.name

            if field.filename:
                files[field.name] = BytesIO(await field.read(decode=False))
            else:
                data[field.name] = await field.text()

        return FormData(files=files, form=data)

    @property
    def content_type(self) -> Optional[str]:
        return self.headers.get("content-type")
    
    @property
    def url(self) -> str:
        return str(self.request.url)
    
    @property
    def cookies(self) -> Mapping[str, str]:
        return self.request.cookies
from __future__ import annotations

from io import BytesIO
from typing import TYPE_CHECKING, Any, Mapping, Optional, cast

from ._base import AsyncHTTPRequestAdapter, FormData, HTTPMethod, QueryParams

if TYPE_CHECKING:
    from aiohttp import web


class AiohttpHTTPRequestAdapter(AsyncHTTPRequestAdapter):
    def __init__(
        self,
        request: web.Request,
        body: Optional[bytes] = None,
        form_data: Optional[FormData] = None,
    ) -> None:
        self.request = request
        self._body = body
        self._form_data = form_data

    @classmethod
    async def create(cls, request: web.Request) -> "AiohttpHTTPRequestAdapter":
        """Create an adapter and pre-read the body to avoid PayloadAccessError"""
        content_type = request.headers.get("content-type", "")
        form_data = None
        body = None

        if content_type.startswith("multipart/form-data"):
            # Pre-process multipart data
            reader = await request.multipart()
            data: dict[str, Any] = {}
            files: dict[str, Any] = {}

            while field := await reader.next():
                from aiohttp.multipart import BodyPartReader

                assert isinstance(field, BodyPartReader)
                assert field.name

                if field.filename:
                    files[field.name] = BytesIO(await field.read(decode=False))
                else:
                    data[field.name] = await field.text()

            form_data = FormData(files=files, form=data)
        else:
            # For non-multipart requests, read the body
            body = await request.read()

        return cls(request, body, form_data)

    @property
    def query_params(self) -> QueryParams:
        return cast(QueryParams, self.request.query.copy())  # type: ignore[attr-defined]

    async def get_body(self) -> bytes:
        if self._form_data is not None:
            return b""
        if self._body is None:
            self._body = await self.request.read()
        return self._body

    @property
    def method(self) -> HTTPMethod:
        return cast("HTTPMethod", self.request.method.upper())

    @property
    def headers(self) -> Mapping[str, str]:
        return self.request.headers

    async def get_form_data(self) -> FormData:
        if self._form_data is not None:
            return self._form_data

        if self.content_type and self.content_type.startswith("multipart/form-data"):
            # Process multipart data
            reader = await self.request.multipart()
            data: dict[str, Any] = {}
            files: dict[str, Any] = {}

            while field := await reader.next():
                from aiohttp.multipart import BodyPartReader

                assert isinstance(field, BodyPartReader)
                assert field.name

                if field.filename:
                    files[field.name] = BytesIO(await field.read(decode=False))
                else:
                    data[field.name] = await field.text()

            self._form_data = FormData(files=files, form=data)
            return self._form_data
        else:
            # For URL-encoded form data
            post_data = await self.request.post()
            return FormData(files={}, form=dict(post_data))

    @property
    def content_type(self) -> Optional[str]:
        return self.headers.get("content-type")

    @property
    def url(self) -> str:
        return str(self.request.url)

    @property
    def cookies(self) -> Mapping[str, str]:
        return self.request.cookies

from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from aiohttp import FormData, web
from aiohttp.test_utils import TestClient, TestServer

from .base import HttpClient, RequestData, Response, UploadedFile


class AiohttpHttpClient(HttpClient):
    def __init__(self, app: web.Application) -> None:
        self.app = app

    def _build_data(
        self,
        data: RequestData | None,
        files: dict[str, UploadedFile] | None,
    ) -> RequestData | FormData | None:
        if not files:
            return data

        if data is not None and not isinstance(data, Mapping):
            raise TypeError("aiohttp multipart requests require mapping form data")

        form_data = FormData()

        for key, value in (data or {}).items():
            form_data.add_field(key, str(value))

        for key, (filename, content, content_type) in files.items():
            form_data.add_field(
                key,
                content,
                filename=filename,
                content_type=content_type or "application/octet-stream",
            )

        return form_data

    async def request(
        self,
        url: str,
        method: str,
        headers: dict[str, str] | None = None,
        **kwargs: Any,
    ) -> Response:
        cookies = kwargs.pop("cookies", None)
        files = kwargs.pop("files", None)
        data = kwargs.pop("data", None)

        if files is not None or data is not None:
            kwargs["data"] = self._build_data(data, files)

        if cookies is not None:
            kwargs["cookies"] = dict(cookies)

        async with TestClient(TestServer(self.app)) as client:
            response = await getattr(client, method)(url, headers=headers, **kwargs)

            return Response(
                status_code=response.status,
                data=await response.read(),
                headers=dict(response.headers),
            )

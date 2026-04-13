from __future__ import annotations

import io
from collections.abc import Mapping
from typing import Any

from quart import Quart
from quart.datastructures import FileStorage

from .base import HttpClient, RequestData, Response, UploadedFile


class QuartHttpClient(HttpClient):
    def __init__(self, app: Quart) -> None:
        self.app = app

    def _build_request_kwargs(
        self,
        data: RequestData | None,
        json_data: object | None,
        files: dict[str, UploadedFile] | None,
        **kwargs: Any,
    ) -> dict[str, Any]:
        request_kwargs = dict(kwargs)

        if json_data is not None:
            request_kwargs["json"] = json_data
            return request_kwargs

        if files is not None:
            if data is not None and not isinstance(data, Mapping):
                raise TypeError("Quart multipart requests require mapping form data")

            request_kwargs["form"] = dict(data or {})
            request_kwargs["files"] = {
                key: FileStorage(
                    stream=io.BytesIO(content),
                    filename=filename,
                    content_type=content_type or "application/octet-stream",
                )
                for key, (filename, content, content_type) in files.items()
            }
            return request_kwargs

        if isinstance(data, Mapping):
            request_kwargs["form"] = dict(data)
        elif data is not None:
            request_kwargs["data"] = data

        return request_kwargs

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
        json_data = kwargs.pop("json", None)
        request_kwargs = self._build_request_kwargs(
            data=data,
            json_data=json_data,
            files=files,
            **kwargs,
        )

        async with self.app.test_app() as test_app, self.app.app_context():
            client = test_app.test_client()
            for key, value in (cookies or {}).items():
                client.set_cookie("localhost", key, value)

            response = await getattr(client, method)(
                url,
                headers=headers,
                **request_kwargs,
            )

        return Response(
            status_code=response.status_code,
            data=await response.get_data(),
            headers=dict(response.headers),
        )

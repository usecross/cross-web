from __future__ import annotations

import asyncio
import contextvars
import functools
import io
from collections.abc import Mapping
from typing import Any

from flask import Flask

from .base import HttpClient, RequestData, Response, UploadedFile


class FlaskHttpClient(HttpClient):
    def __init__(self, app: Flask) -> None:
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

        if files is None:
            if data is not None:
                request_kwargs["data"] = data
            return request_kwargs

        if data is not None and not isinstance(data, Mapping):
            raise TypeError("Flask multipart requests require mapping form data")

        multipart_data = dict(data or {})
        for key, (filename, content, content_type) in files.items():
            multipart_data[key] = (
                io.BytesIO(content),
                filename,
                content_type or "application/octet-stream",
            )

        request_kwargs["data"] = multipart_data
        return request_kwargs

    def _do_request(
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

        with self.app.test_client() as client:
            for key, value in (cookies or {}).items():
                client.set_cookie(key, value)

            response = client.open(
                url,
                method=method.upper(),
                headers=headers,
                **request_kwargs,
            )

        return Response(
            status_code=response.status_code,
            data=response.data,
            headers=dict(response.headers),
        )

    async def request(
        self,
        url: str,
        method: str,
        headers: dict[str, str] | None = None,
        **kwargs: Any,
    ) -> Response:
        loop = asyncio.get_running_loop()
        ctx = contextvars.copy_context()
        func_call = functools.partial(
            ctx.run,
            self._do_request,
            url=url,
            method=method,
            headers=headers,
            **kwargs,
        )
        return await loop.run_in_executor(None, func_call)


class AsyncFlaskHttpClient(FlaskHttpClient):
    pass

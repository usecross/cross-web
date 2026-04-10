from __future__ import annotations

import json
from typing import Any

from chalice.app import Chalice
from chalice.test import Client

from .base import HttpClient, Response, merge_cookies


class ChaliceHttpClient(HttpClient):
    supports_form_data = False

    def __init__(self, app: Chalice) -> None:
        self.app = app

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

        if files is not None:
            raise NotImplementedError("Chalice test client does not support files")

        request_headers = merge_cookies(headers, cookies)
        body: str | bytes | None = None

        if json_data is not None:
            body = json.dumps(json_data)
            request_headers = dict(request_headers or {})
            request_headers.setdefault("Content-Type", "application/json")
        elif isinstance(data, (bytes, str)):
            body = data
        elif data is not None:
            raise NotImplementedError("Chalice test client does not support form data")

        request_kwargs = {"headers": request_headers, **kwargs}
        if body is not None:
            request_kwargs["body"] = body

        with Client(self.app) as client:
            response = getattr(client.http, method)(url, **request_kwargs)

        response_body = response.body
        if isinstance(response_body, str):
            response_body = response_body.encode()

        return Response(
            status_code=response.status_code,
            data=response_body,
            headers=dict(response.headers),
        )

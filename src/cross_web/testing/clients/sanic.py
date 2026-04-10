from __future__ import annotations

from typing import Any

from .base import HttpClient, Response, merge_cookies


class SanicHttpClient(HttpClient):
    def __init__(self, app: Any) -> None:
        self.app = app

    async def request(
        self,
        url: str,
        method: str,
        headers: dict[str, str] | None = None,
        **kwargs: Any,
    ) -> Response:
        cookies = kwargs.pop("cookies", None)
        request_headers = merge_cookies(headers, cookies)

        _, response = await self.app.asgi_client.request(
            method.upper(),
            url,
            headers=request_headers,
            **kwargs,
        )

        return Response(
            status_code=response.status,
            data=response.body,
            headers=dict(response.headers),
        )

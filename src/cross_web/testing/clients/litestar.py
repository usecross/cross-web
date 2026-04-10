from __future__ import annotations

from typing import Any

from litestar import Litestar
from litestar.testing import TestClient

from .base import HttpClient, Response


class LitestarHttpClient(HttpClient):
    def __init__(self, app: Litestar) -> None:
        self.app = app

    async def request(
        self,
        url: str,
        method: str,
        headers: dict[str, str] | None = None,
        **kwargs: Any,
    ) -> Response:
        cookies = kwargs.pop("cookies", None)

        with TestClient(app=self.app) as client:
            client.cookies.update(dict(cookies or {}))
            response = client.request(
                method.upper(),
                url,
                headers=headers,
                **kwargs,
            )

        return Response(
            status_code=response.status_code,
            data=response.content,
            headers=dict(response.headers),
        )

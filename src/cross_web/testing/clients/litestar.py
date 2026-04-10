from __future__ import annotations

import json

from litestar import Litestar, Request, post
from litestar.testing import TestClient

from cross_web.request._litestar import LitestarRequestAdapter

from .base import (
    FormRequestResult,
    JSONRequestResult,
    RequestClient,
    build_form_result,
    build_json_result,
    get_content_type,
    normalize_cookies,
)


class LitestarRequestClient(RequestClient):
    async def json_request(self) -> JSONRequestResult:
        @post("/json/{item_id:str}")  # type: ignore[misc]
        async def handler(request: Request) -> dict[str, object]:
            adapter = LitestarRequestAdapter(request)
            body = await adapter.get_body()

            return {
                "query_params": dict(adapter.query_params),
                "method": adapter.method,
                "header_content_type": get_content_type(dict(adapter.headers)),
                "content_type": adapter.content_type,
                "url": adapter.url,
                "cookies": normalize_cookies(dict(adapter.cookies)),
                "body_json": json.loads(body.decode()),
            }

        app = Litestar([handler])

        with TestClient(app=app) as client:
            client.cookies["session"] = "123"
            response = client.post("/json/abc?query=test", json={"key": "value"})

        return build_json_result(response.json())

    async def form_request(self) -> FormRequestResult:
        @post("/form/{item_id:str}")  # type: ignore[misc]
        async def handler(request: Request) -> dict[str, object]:
            adapter = LitestarRequestAdapter(request)
            form_data = await adapter.get_form_data()

            return {
                "query_params": dict(adapter.query_params),
                "method": adapter.method,
                "header_content_type": get_content_type(dict(adapter.headers)),
                "content_type": adapter.content_type,
                "url": adapter.url,
                "cookies": normalize_cookies(dict(adapter.cookies)),
                "form_value": form_data.form["form"],
                "has_file": "file" in form_data.files,
            }

        app = Litestar([handler])

        with TestClient(app=app) as client:
            client.cookies["session"] = "123"
            response = client.post(
                "/form/abc?query=test",
                data={"form": "data"},
                files={"file": ("test.txt", b"upload")},
            )

        return build_form_result(response.json())

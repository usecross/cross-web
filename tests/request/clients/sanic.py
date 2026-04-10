from __future__ import annotations

import json
import uuid

from sanic import Sanic
from sanic.request import Request
from sanic.response import json as sanic_json

from cross_web import SanicHTTPRequestAdapter

from .base import (
    FormRequestResult,
    JSONRequestResult,
    RequestClient,
    build_form_result,
    build_json_result,
    get_content_type,
    normalize_cookies,
)


class SanicRequestClient(RequestClient):
    def __init__(self) -> None:
        self.app: Sanic[object, object] = Sanic(f"CrossWeb_{uuid.uuid4().hex[:8]}")

        @self.app.post("/json/<item_id>")  # type: ignore[misc]
        async def json_handler(request: Request, item_id: str):
            adapter = SanicHTTPRequestAdapter(request)
            body = await adapter.get_body()

            return sanic_json(
                {
                    "query_params": dict(adapter.query_params),
                    "method": adapter.method,
                    "header_content_type": get_content_type(dict(adapter.headers)),
                    "content_type": adapter.content_type,
                    "url": adapter.url,
                    "cookies": normalize_cookies(dict(adapter.cookies)),
                    "body_json": json.loads(body.decode()),
                }
            )

        @self.app.post("/form/<item_id>")  # type: ignore[misc]
        async def form_handler(request: Request, item_id: str):
            adapter = SanicHTTPRequestAdapter(request)
            form_data = await adapter.get_form_data()

            return sanic_json(
                {
                    "query_params": dict(adapter.query_params),
                    "method": adapter.method,
                    "header_content_type": get_content_type(dict(adapter.headers)),
                    "content_type": adapter.content_type,
                    "url": adapter.url,
                    "cookies": normalize_cookies(dict(adapter.cookies)),
                    "form_value": form_data.form["form"],
                    "has_file": "textFile" in form_data.files,
                }
            )

    async def json_request(self) -> JSONRequestResult:
        self.app.asgi_client.cookies["session"] = "123"
        _, response = await self.app.asgi_client.post(
            "/json/abc?query=test", json={"key": "value"}
        )
        return build_json_result(response.json)

    async def form_request(self) -> FormRequestResult:
        self.app.asgi_client.cookies["session"] = "123"
        _, response = await self.app.asgi_client.post(
            "/form/abc?query=test",
            data={"form": "data"},
            files={"textFile": ("textFile.txt", b"upload", "text/plain")},
        )
        return build_form_result(response.json)

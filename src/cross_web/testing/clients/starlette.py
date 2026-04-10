from __future__ import annotations

import io
import json

from starlette.applications import Starlette
from starlette.responses import JSONResponse
from starlette.routing import Route
from starlette.testclient import TestClient

from cross_web.request._starlette import StarletteRequestAdapter

from .base import (
    FormRequestResult,
    JSONRequestResult,
    RequestClient,
    build_form_result,
    build_json_result,
    get_content_type,
    normalize_cookies,
)


class StarletteRequestClient(RequestClient):
    async def json_request(self) -> JSONRequestResult:
        async def handler(request) -> JSONResponse:
            adapter = StarletteRequestAdapter(request)
            body = await adapter.get_body()

            return JSONResponse(
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

        app = Starlette(routes=[Route("/json/{item_id}", handler, methods=["POST"])])

        with TestClient(app) as client:
            client.cookies.set("session", "123")
            response = client.post("/json/abc?query=test", json={"key": "value"})

        return build_json_result(response.json())

    async def form_request(self) -> FormRequestResult:
        async def handler(request) -> JSONResponse:
            adapter = StarletteRequestAdapter(request)
            form_data = await adapter.get_form_data()

            return JSONResponse(
                {
                    "query_params": dict(adapter.query_params),
                    "method": adapter.method,
                    "header_content_type": get_content_type(dict(adapter.headers)),
                    "content_type": adapter.content_type,
                    "url": adapter.url,
                    "cookies": normalize_cookies(dict(adapter.cookies)),
                    "form_value": form_data.form["form"],
                    "has_file": "file" in form_data.files,
                }
            )

        app = Starlette(routes=[Route("/form/{item_id}", handler, methods=["POST"])])

        with TestClient(app) as client:
            client.cookies.set("session", "123")
            response = client.post(
                "/form/abc?query=test",
                data={"form": "data"},
                files={"file": ("test.txt", io.BytesIO(b"upload"), "text/plain")},
            )

        return build_form_result(response.json())

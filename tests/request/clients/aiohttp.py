from __future__ import annotations

import json

from aiohttp import FormData, web
from aiohttp.test_utils import TestClient, TestServer

from cross_web import AiohttpHTTPRequestAdapter

from .base import (
    RequestClient,
    JSONRequestResult,
    FormRequestResult,
    build_form_result,
    build_json_result,
    get_content_type,
    normalize_cookies,
)


class AiohttpRequestClient(RequestClient):
    async def json_request(self) -> JSONRequestResult:
        async def handler(request: web.Request) -> web.Response:
            adapter = await AiohttpHTTPRequestAdapter.create(request)
            body = await adapter.get_body()

            return web.json_response(
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

        app = web.Application()
        app.router.add_post("/json/{item_id}", handler)

        async with TestClient(TestServer(app)) as client:
            response = await client.post(
                "/json/abc?query=test",
                json={"key": "value"},
                cookies={"session": "123"},
            )

            return build_json_result(await response.json())

    async def form_request(self) -> FormRequestResult:
        async def handler(request: web.Request) -> web.Response:
            adapter = await AiohttpHTTPRequestAdapter.create(request)
            form_data = await adapter.get_form_data()

            return web.json_response(
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

        app = web.Application()
        app.router.add_post("/form/{item_id}", handler)

        async with TestClient(TestServer(app)) as client:
            data = FormData()
            data.add_field("form", "data")
            data.add_field(
                "file", b"upload", filename="test.txt", content_type="text/plain"
            )
            response = await client.post(
                "/form/abc?query=test",
                data=data,
                cookies={"session": "123"},
            )

            return build_form_result(await response.json())

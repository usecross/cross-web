from __future__ import annotations

import asyncio
import contextvars
import functools
import io
import json

from flask import Flask, request

from cross_web.request._flask import (
    AsyncFlaskHTTPRequestAdapter,
    FlaskHTTPRequestAdapter,
)

from .base import (
    FormRequestResult,
    JSONRequestResult,
    RequestClient,
    build_form_result,
    build_json_result,
    get_content_type,
)


class FlaskRequestClient(RequestClient):
    def __init__(self) -> None:
        self.app = Flask(__name__)

        @self.app.post("/sync/json/<item_id>")
        def json_handler(item_id: str) -> dict[str, object]:
            adapter = FlaskHTTPRequestAdapter(request)

            return {
                "query_params": dict(adapter.query_params),
                "method": adapter.method,
                "header_content_type": get_content_type(dict(adapter.headers)),
                "content_type": adapter.content_type,
                "url": adapter.url,
                "cookies": dict(adapter.cookies),
                "body_json": json.loads(adapter.body),
            }

        @self.app.post("/sync/form/<item_id>")
        def form_handler(item_id: str) -> dict[str, object]:
            adapter = FlaskHTTPRequestAdapter(request)
            form_data = adapter.get_form_data()

            return {
                "query_params": dict(adapter.query_params),
                "method": adapter.method,
                "header_content_type": get_content_type(dict(adapter.headers)),
                "content_type": adapter.content_type,
                "url": adapter.url,
                "cookies": dict(adapter.cookies),
                "form_value": form_data.form["form"],
                "has_file": "file" in form_data.files,
                "post_form_value": adapter.post_data["form"],
                "files_has_file": "file" in adapter.files,
            }

    async def json_request(self) -> JSONRequestResult:
        with self.app.test_client() as client:
            client.set_cookie("session", "123")
            response = client.post(
                "/sync/json/abc?query=test",
                data=json.dumps({"key": "value"}),
                content_type="application/json",
            )

        return build_json_result(response.get_json())

    async def form_request(self) -> FormRequestResult:
        with self.app.test_client() as client:
            client.set_cookie("session", "123")
            response = client.post(
                "/sync/form/abc?query=test",
                data={"form": "data", "file": (io.BytesIO(b"upload"), "test.txt")},
            )

        return build_form_result(response.get_json())


class AsyncFlaskRequestClient(RequestClient):
    def __init__(self) -> None:
        self.app = Flask(__name__)

        @self.app.post("/async/json/<item_id>")
        async def json_handler(item_id: str) -> dict[str, object]:
            adapter = AsyncFlaskHTTPRequestAdapter(request)
            body = await adapter.get_body()

            return {
                "query_params": dict(adapter.query_params),
                "method": adapter.method,
                "header_content_type": get_content_type(dict(adapter.headers)),
                "content_type": adapter.content_type,
                "url": adapter.url,
                "cookies": dict(adapter.cookies),
                "body_json": json.loads(body.decode()),
            }

        @self.app.post("/async/form/<item_id>")
        async def form_handler(item_id: str) -> dict[str, object]:
            adapter = AsyncFlaskHTTPRequestAdapter(request)
            form_data = await adapter.get_form_data()

            return {
                "query_params": dict(adapter.query_params),
                "method": adapter.method,
                "header_content_type": get_content_type(dict(adapter.headers)),
                "content_type": adapter.content_type,
                "url": adapter.url,
                "cookies": dict(adapter.cookies),
                "form_value": form_data.form["form"],
                "has_file": "file" in form_data.files,
            }

    def _do_json_request(self) -> dict[str, object] | None:
        with self.app.test_client() as client:
            client.set_cookie("session", "123")
            response = client.post(
                "/async/json/abc?query=test",
                data=json.dumps({"key": "value"}),
                content_type="application/json",
            )

        return response.get_json()

    async def json_request(self) -> JSONRequestResult:
        loop = asyncio.get_running_loop()
        ctx = contextvars.copy_context()
        result = await loop.run_in_executor(
            None, functools.partial(ctx.run, self._do_json_request)
        )

        return build_json_result(result)

    def _do_form_request(self) -> dict[str, object] | None:
        with self.app.test_client() as client:
            client.set_cookie("session", "123")
            response = client.post(
                "/async/form/abc?query=test",
                data={"form": "data", "file": (io.BytesIO(b"upload"), "test.txt")},
            )

        return response.get_json()

    async def form_request(self) -> FormRequestResult:
        loop = asyncio.get_running_loop()
        ctx = contextvars.copy_context()
        result = await loop.run_in_executor(
            None, functools.partial(ctx.run, self._do_form_request)
        )

        return build_form_result(result)

from __future__ import annotations

import io
import json

from quart import Quart, request
from werkzeug.datastructures import FileStorage

from cross_web import QuartHTTPRequestAdapter

from .base import (
    FormRequestResult,
    JSONRequestResult,
    RequestClient,
    build_form_result,
    build_json_result,
    get_content_type,
)


class QuartRequestClient(RequestClient):
    def __init__(self) -> None:
        self.app = Quart(__name__)

        @self.app.post("/json/<item_id>")  # type: ignore[misc]
        async def json_handler(item_id: str) -> dict[str, object]:
            adapter = QuartHTTPRequestAdapter(request)
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

        @self.app.post("/form/<item_id>")  # type: ignore[misc]
        async def form_handler(item_id: str) -> dict[str, object]:
            adapter = QuartHTTPRequestAdapter(request)
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

    async def json_request(self) -> JSONRequestResult:
        async with self.app.test_app() as test_app, self.app.app_context():
            client = test_app.test_client()
            client.set_cookie("localhost", "session", "123")
            response = await client.post("/json/abc?query=test", json={"key": "value"})

        return build_json_result(await response.get_json())

    async def form_request(self) -> FormRequestResult:
        async with self.app.test_app() as test_app, self.app.app_context():
            client = test_app.test_client()
            client.set_cookie("localhost", "session", "123")
            file_obj = FileStorage(
                stream=io.BytesIO(b"upload"),
                filename="test.txt",
                content_type="text/plain",
            )
            response = await client.post(
                "/form/abc?query=test",
                form={"form": "data"},
                files={"file": file_obj},
            )

        return build_form_result(await response.get_json())

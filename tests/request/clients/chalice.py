from __future__ import annotations

import json

from chalice.app import Chalice
from chalice.test import Client

from cross_web import ChaliceHTTPRequestAdapter

from .base import JSONRequestResult, RequestClient, build_json_result, get_content_type


class ChaliceRequestClient(RequestClient):
    supports_form_data = False

    def __init__(self) -> None:
        self.app = Chalice(app_name="cross_web_tests")

        @self.app.route(
            "/json/{item_id}", methods=["POST"], content_types=["application/json"]
        )
        def json_handler(item_id: str) -> dict[str, object]:
            assert self.app.current_request is not None
            adapter = ChaliceHTTPRequestAdapter(self.app.current_request)

            return {
                "query_params": dict(adapter.query_params),
                "method": adapter.method,
                "header_content_type": get_content_type(dict(adapter.headers)),
                "content_type": adapter.content_type,
                "url": adapter.url,
                "cookies": dict(adapter.cookies),
                "body_json": json.loads(adapter.body.decode()),
            }

    async def json_request(self) -> JSONRequestResult:
        with Client(self.app) as client:
            response = client.http.post(
                "/json/abc?query=test",
                headers={"Content-Type": "application/json", "Cookie": "session=123"},
                body=json.dumps({"key": "value"}),
            )

        return build_json_result(json.loads(response.body))

    async def form_request(self):
        raise NotImplementedError

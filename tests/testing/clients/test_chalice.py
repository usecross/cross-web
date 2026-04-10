from __future__ import annotations

from types import SimpleNamespace
from typing import cast

import pytest
from chalice.app import Chalice

from cross_web.testing.clients import chalice as chalice_client_module
from cross_web.testing.clients.chalice import ChaliceHttpClient

pytestmark = [pytest.mark.chalice]


class FakeClientContext:
    def __init__(self, response_body: str) -> None:
        self.captured: dict[str, object] = {}
        self.response = SimpleNamespace(
            status_code=200,
            headers={"Content-Type": "text/plain"},
            body=response_body,
        )

    def __enter__(self) -> SimpleNamespace:
        def post(url: str, **kwargs: object) -> SimpleNamespace:
            self.captured = {"url": url, **kwargs}
            return self.response

        return SimpleNamespace(http=SimpleNamespace(post=post))

    def __exit__(self, exc_type: object, exc: object, tb: object) -> None:
        return None


@pytest.mark.asyncio
async def test_request_handles_bytes_body_and_string_response(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    fake_client = FakeClientContext(response_body="ok")
    monkeypatch.setattr(chalice_client_module, "Client", lambda app: fake_client)

    client = ChaliceHttpClient(cast(Chalice, object()))

    response = await client.request(
        "/request",
        "post",
        headers={"X-Test": "1"},
        data=b"payload",
    )

    assert fake_client.captured["body"] == b"payload"
    assert response.data == b"ok"
    assert response.headers["content-type"] == "text/plain"


@pytest.mark.asyncio
async def test_request_rejects_files() -> None:
    client = ChaliceHttpClient(cast(Chalice, object()))

    with pytest.raises(NotImplementedError, match="does not support files"):
        await client.request(
            "/request",
            "post",
            files={"file": ("test.txt", b"payload", "text/plain")},
        )


@pytest.mark.asyncio
async def test_request_rejects_form_data() -> None:
    client = ChaliceHttpClient(cast(Chalice, object()))

    with pytest.raises(NotImplementedError, match="does not support form data"):
        await client.request("/request", "post", data={"field": "value"})

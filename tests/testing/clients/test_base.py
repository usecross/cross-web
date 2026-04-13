from __future__ import annotations

from typing import Any, cast

import pytest

from cross_web.testing.clients.base import HttpClient, Response, merge_cookies


class DummyHttpClient:
    def __init__(self, app: Any) -> None:
        self.app = app
        self.calls: list[tuple[str, str, dict[str, str] | None, dict[str, Any]]] = []

    async def request(
        self,
        url: str,
        method: str,
        headers: dict[str, str] | None = None,
        **kwargs: Any,
    ) -> Response:
        self.calls.append((url, method, headers, kwargs))
        return Response(
            status_code=200,
            data=b'{"ok": true}',
            headers={"Content-Type": "application/json"},
        )


def test_response_properties() -> None:
    response = Response(
        status_code=200,
        data=b'{"ok": true}',
        headers={"Content-Type": "application/json"},
    )

    assert response.headers == {"content-type": "application/json"}
    assert response.text == '{"ok": true}'
    assert response.json == {"ok": True}


@pytest.mark.asyncio
async def test_http_client_get_delegates_to_request() -> None:
    client = DummyHttpClient(app=None)

    await HttpClient.get(
        cast(Any, client), "/ping", headers={"X-Test": "1"}, query="value"
    )

    assert client.calls == [
        ("/ping", "get", {"X-Test": "1"}, {"query": "value"}),
    ]


@pytest.mark.asyncio
async def test_http_client_post_delegates_to_request() -> None:
    client = DummyHttpClient(app=None)

    await HttpClient.post(
        cast(Any, client),
        "/submit",
        data=b"payload",
        json={"ok": True},
        files={"file": ("test.txt", b"body", "text/plain")},
        headers={"X-Test": "1"},
        query="value",
    )

    assert client.calls == [
        (
            "/submit",
            "post",
            {"X-Test": "1"},
            {
                "data": b"payload",
                "json": {"ok": True},
                "files": {"file": ("test.txt", b"body", "text/plain")},
                "query": "value",
            },
        ),
    ]


def test_merge_cookies_handles_missing_and_present_cookies() -> None:
    assert merge_cookies(None, None) is None
    assert merge_cookies({"X-Test": "1"}, {"session": "abc"}) == {
        "X-Test": "1",
        "Cookie": "session=abc",
    }


def test_merge_cookies_merges_existing_cookie_header() -> None:
    assert merge_cookies(
        {"X-Test": "1", "Cookie": "session=old; theme=dark"},
        {"session": "new", "user": "patrick"},
    ) == {
        "X-Test": "1",
        "Cookie": "session=new; theme=dark; user=patrick",
    }

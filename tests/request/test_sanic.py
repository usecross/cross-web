from __future__ import annotations

import pytest
from typing import TYPE_CHECKING, Any

from cross_web import SanicHTTPRequestAdapter

pytestmark = [pytest.mark.sanic]

if TYPE_CHECKING:
    from sanic import Sanic
    from sanic.request import Request
    from sanic.response import HTTPResponse


@pytest.fixture
def app() -> Sanic[Any, Any]:
    import uuid
    from sanic import Sanic

    # Use a unique name to avoid conflicts between tests
    return Sanic(f"TestSanic_{uuid.uuid4().hex[:8]}")


@pytest.mark.asyncio
async def test_sanic_adapter(app: Sanic[Any, Any]) -> None:
    from sanic.response import text

    adapter_result = None

    @app.post("/test")  # type: ignore[misc]
    async def handler(request: Request) -> HTTPResponse:
        nonlocal adapter_result
        adapter_result = SanicHTTPRequestAdapter(request)
        return text("OK")

    # Test with form data and files
    app.asgi_client.cookies["session"] = "123"
    _, response = await app.asgi_client.post(
        "/test?query=test",
        data={"form": "data"},
        files={"textFile": ("textFile.txt", b"upload", "text/plain")},
    )

    assert adapter_result is not None
    assert adapter_result.query_params == {"query": "test"}
    body = await adapter_result.get_body()
    assert body  # Body contains multipart data
    assert adapter_result.method == "POST"
    assert adapter_result.headers["content-type"].startswith("multipart/form-data")
    assert (
        adapter_result.content_type is not None
        and adapter_result.content_type.startswith("multipart/form-data")
    )
    assert "test" in adapter_result.url
    # Sanic cookies are returned as lists
    assert adapter_result.cookies["session"] == "123" or adapter_result.cookies == {
        "session": ["123"]
    }

    form_data = await adapter_result.get_form_data()
    # Sanic form data values are lists
    assert form_data.form["form"] == ["data"] or form_data.form["form"] == "data"
    assert "textFile" in form_data.files


@pytest.mark.asyncio
async def test_sanic_adapter_json(app: Sanic[Any, Any]) -> None:
    from sanic.response import text

    adapter_result = None

    @app.post("/test")  # type: ignore[misc]
    async def handler(request: Request) -> HTTPResponse:
        nonlocal adapter_result
        adapter_result = SanicHTTPRequestAdapter(request)
        return text("OK")

    # Test with JSON data
    app.asgi_client.cookies["session"] = "123"
    _, response = await app.asgi_client.post("/test?query=test", json={"key": "value"})

    assert adapter_result is not None
    assert adapter_result.query_params == {"query": "test"}
    body = await adapter_result.get_body()
    assert body == b'{"key":"value"}'
    assert adapter_result.method == "POST"
    assert adapter_result.headers["content-type"] == "application/json"
    assert adapter_result.content_type == "application/json"
    assert "test" in adapter_result.url
    # Sanic cookies are returned as lists
    assert adapter_result.cookies["session"] == "123" or adapter_result.cookies == {
        "session": ["123"]
    }

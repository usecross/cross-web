from __future__ import annotations

from typing import TYPE_CHECKING
import pytest

from cross_web import StarletteRequestAdapter

pytestmark = [pytest.mark.starlette]

if TYPE_CHECKING:
    from starlette.requests import Request


@pytest.mark.asyncio
async def test_starlette_adapter() -> None:
    from starlette.applications import Starlette
    from starlette.responses import JSONResponse
    from starlette.routing import Route
    from starlette.testclient import TestClient

    adapter_result = None
    body_result = None

    async def handler(request: Request) -> JSONResponse:
        nonlocal adapter_result, body_result
        adapter_result = StarletteRequestAdapter(request)
        body_result = await adapter_result.get_body()
        return JSONResponse({"status": "ok"})

    app = Starlette(routes=[Route("/test", handler, methods=["POST"])])

    with TestClient(app) as client:
        client.cookies.set("session", "123")
        client.post("/test?query=test", json={"key": "value"})

        assert adapter_result is not None
        assert dict(adapter_result.query_params) == {"query": "test"}
        assert adapter_result.method == "POST"
        assert adapter_result.headers["content-type"] == "application/json"
        assert adapter_result.content_type == "application/json"
        assert "test" in str(adapter_result.url)
        assert dict(adapter_result.cookies) == {"session": "123"}
        assert body_result == b'{"key":"value"}'  # JSON encoding removes spaces


@pytest.mark.asyncio
async def test_starlette_adapter_form_data() -> None:
    from starlette.applications import Starlette
    from starlette.responses import JSONResponse
    from starlette.routing import Route
    from starlette.testclient import TestClient
    import io

    adapter_result = None
    form_data_result = None

    async def handler(request: Request) -> JSONResponse:
        nonlocal adapter_result, form_data_result
        adapter_result = StarletteRequestAdapter(request)
        form_data_result = await adapter_result.get_form_data()
        return JSONResponse({"status": "ok"})

    app = Starlette(routes=[Route("/test", handler, methods=["POST"])])

    with TestClient(app) as client:
        client.cookies.set("session", "123")
        client.post(
            "/test?query=test",
            data={"form": "data"},
            files={"file": ("test.txt", io.BytesIO(b"upload"), "text/plain")},
        )

        assert adapter_result is not None
        assert dict(adapter_result.query_params) == {"query": "test"}
        assert adapter_result.method == "POST"
        assert adapter_result.headers[
            "content-type"
        ] is not None and adapter_result.headers["content-type"].startswith(
            "multipart/form-data"
        )
        assert (
            adapter_result.content_type is not None
            and adapter_result.content_type.startswith("multipart/form-data")
        )
        assert "test" in str(adapter_result.url)
        assert dict(adapter_result.cookies) == {"session": "123"}

        # Check form data was retrieved
        assert form_data_result is not None
        assert "form" in form_data_result.form
        assert "file" in form_data_result.files
